"""Step 4: agentic distillation (SFT warm start) through AgentTune's create_distill_trainer.

Teacher = our evidence-only solver (artifacts/sft-data). A custom trainer_factory keeps AgentTune's distillation
pipeline but trains only on the assistant action (prompt/completion format), not on the 4k-token observation."""
import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from baseline.interface_v3 import SYSTEM


def load_rows(paths, per_room_cap, seed):
    """Stratified subsample: cap rows per (room, tool) so movement steps don't drown the hard decisions."""
    rows = []
    for p in paths:
        with open(p) as f:
            rows += [json.loads(l) for l in f]
    rng = random.Random(seed)
    rng.shuffle(rows)
    buckets = defaultdict(list)
    for r in rows:
        tool = json.loads(r["messages"][-1]["content"])["tool"]
        buckets[(r["room"], tool)].append(r)
    picked = []
    for key, items in buckets.items():
        picked += items[:per_room_cap]
    rng.shuffle(picked)
    return picked


class CompletionOnlyFactory:
    """AgentTune trainer_factory: LoRA + TRL SFTTrainer on prompt/completion pairs (loss on completion only)."""
    def __init__(self, rows, lora_r=32, lora_alpha=64, max_length=6144, init_adapter=None):
        self.rows, self.lora_r, self.lora_alpha, self.max_length = rows, lora_r, lora_alpha, max_length
        self.init_adapter = init_adapter

    def __call__(self, *, model, train_dataset, **kwargs):
        import torch
        from datasets import Dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from trl import SFTConfig, SFTTrainer
        tok = AutoTokenizer.from_pretrained(model)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        cuda = torch.cuda.is_available()
        bf16 = cuda and torch.cuda.is_bf16_supported()
        net = AutoModelForCausalLM.from_pretrained(model, dtype=torch.bfloat16 if bf16 else (torch.float16 if cuda else torch.float32))
        # TRL truncates from the right, which would silently delete the completion (zero loss). Measure every row
        # with the real chat template and drop any that do not fit, instead of training on empty targets.
        kept, dropped, lengths = [], 0, []
        for r in self.rows:
            ids = tok.apply_chat_template(r["messages"], tokenize=True)
            ids = ids["input_ids"] if hasattr(ids, "keys") else ids  # transformers 5 returns a BatchEncoding
            n = len(ids)
            lengths.append(n)
            if n <= self.max_length:
                kept.append(r)
            else:
                dropped += 1
        lengths.sort()
        self.length_stats = {"kept": len(kept), "dropped_too_long": dropped, "tokens_p50": lengths[len(lengths)//2],
                             "tokens_p95": lengths[int(len(lengths)*.95)], "tokens_max": lengths[-1]}
        print("length check:", self.length_stats, flush=True)
        if not kept:
            raise RuntimeError("no training rows fit max_length")
        data = Dataset.from_list([{"prompt": r["messages"][:-1], "completion": [r["messages"][-1]]} for r in kept])
        cfg = SFTConfig(max_length=self.max_length, completion_only_loss=True, bf16=bf16, fp16=cuda and not bf16,
                        gradient_checkpointing=cuda, report_to=[], **kwargs)
        peft = LoraConfig(r=self.lora_r, lora_alpha=self.lora_alpha, lora_dropout=0.05, task_type="CAUSAL_LM",
                          target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
        if self.init_adapter:  # continue training an existing LoRA (SFT v1 -> v2) instead of a fresh one
            from peft import PeftModel
            net = PeftModel.from_pretrained(net, self.init_adapter, is_trainable=True)
            n_train = sum(p.numel() for p in net.parameters() if p.requires_grad)
            print("continuing adapter", self.init_adapter, "trainable params", n_train, flush=True)
            if n_train == 0:
                raise RuntimeError("init adapter loaded without trainable parameters")
            peft = None
        self.trainer = SFTTrainer(model=net, args=cfg, train_dataset=data, processing_class=tok, peft_config=peft)
        self.tokenizer = tok
        return self.trainer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="CohereLabs/tiny-aya-global")
    p.add_argument("--data", nargs="+", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--per-bucket", type=int, default=120)
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--accum", type=int, default=16)
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--max-length", type=int, default=6144)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--init-adapter", default=None)
    a = p.parse_args()
    from agenttune.agentic.distill_trainer import create_distill_trainer
    rows = load_rows(a.data, a.per_bucket, a.seed)
    stats = {"rows": len(rows), "by_room": dict(sorted(Counter(r["room"] for r in rows).items())),
             "by_tool": dict(Counter(json.loads(r["messages"][-1]["content"])["tool"] for r in rows).most_common())}
    print(json.dumps(stats))
    total = a.max_steps if a.max_steps > 0 else max(1, int(len(rows) * a.epochs / (a.batch * a.accum)))
    warmup = max(1, int(0.05 * total)) if total >= 20 else 0  # never let warmup swallow a short run
    stats.update(total_steps=total, warmup_steps=warmup)
    factory = CompletionOnlyFactory(rows, max_length=a.max_length, init_adapter=a.init_adapter)
    demos = [{"prompt": r["messages"][1]["content"], "response": r["messages"][-1]["content"]} for r in rows]
    trainer = create_distill_trainer(a.model, demonstrations=demos, system_prompt=SYSTEM, trainer_factory=factory,
                                     output_dir=a.output, num_train_epochs=a.epochs, learning_rate=a.lr,
                                     per_device_train_batch_size=a.batch, gradient_accumulation_steps=a.accum,
                                     max_steps=a.max_steps, warmup_steps=warmup, lr_scheduler_type="cosine",
                                     logging_steps=5, save_strategy="no", seed=a.seed)
    result = trainer.train()
    factory.trainer.save_model(a.output)
    factory.tokenizer.save_pretrained(a.output)
    hist = factory.trainer.state.log_history
    stats["length_check"] = getattr(factory, "length_stats", None)
    Path(a.output, "train_log.json").write_text(json.dumps({"stats": stats, "log_history": hist}, indent=1, default=str))
    losses = [float(h.get("loss", h.get("train_loss"))) for h in hist if ("loss" in h or "train_loss" in h)]
    if hist and (not losses or max(losses) == 0):
        raise RuntimeError("training produced zero loss: targets are empty")
    print(json.dumps({"final_loss": [h.get("loss") for h in hist if "loss" in h][-3:], "result": str(result)[:300]}))


if __name__ == "__main__":
    main()
