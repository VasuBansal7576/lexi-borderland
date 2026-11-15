"""Step 5: GRPO through AgentTune's create_agentic_trainer with the verifiable Borderland step reward.
--control uses the action-independent random reward (control arm for Gate D)."""
import argparse
import json
import random
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="merged SFT model (or base)")
    p.add_argument("--states", nargs="+", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--control", action="store_true")
    p.add_argument("--max-states", type=int, default=2000)
    p.add_argument("--steps", type=int, default=150)
    p.add_argument("--generations", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--beta", type=float, default=0.0)
    p.add_argument("--completion-len", type=int, default=512)
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--max-prompt-tokens", type=int, default=6000)
    p.add_argument("--save-steps", type=int, default=10**9)
    a = p.parse_args()
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoTokenizer
    from agenttune import create_agentic_trainer
    from .reward import borderland_step_reward, random_control_reward

    tok = AutoTokenizer.from_pretrained(a.model)
    rows = []
    for path in a.states:
        rows += [json.loads(l) for l in open(path)]
    rng = random.Random(a.seed); rng.shuffle(rows)
    kept = []
    for r in rows:
        ids = tok.apply_chat_template(r["prompt"], tokenize=True, add_generation_prompt=True)
        ids = ids["input_ids"] if hasattr(ids, "keys") else ids
        if len(ids) <= a.max_prompt_tokens:
            kept.append({k: r[k] for k in ("prompt", "world", "prefix", "facts", "room", "teacher_tool")})
        if len(kept) >= a.max_states:
            break
    data = Dataset.from_list(kept)
    cuda = torch.cuda.is_available()
    peft = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    want = dict(output_dir=a.output, max_steps=a.steps, learning_rate=a.lr, beta=a.beta,
                num_generations=a.generations, per_device_train_batch_size=a.batch,
                gradient_accumulation_steps=max(1, a.generations // a.batch),
                generation_batch_size=a.generations,  # generate one group at a time
                max_completion_length=a.completion_len, temperature=a.temperature,
                warmup_steps=max(1, a.steps // 20) if a.steps >= 20 else 0, logging_steps=1, save_steps=a.save_steps,
                bf16=cuda and torch.cuda.is_bf16_supported(), fp16=cuda and not torch.cuda.is_bf16_supported(),
                gradient_checkpointing=cuda, seed=a.seed, report_to=[], log_completions=False)
    trainer = create_agentic_trainer("grpo", backend="trl", model=a.model, processing_class=tok,
                                     reward_funcs=[random_control_reward if a.control else borderland_step_reward],
                                     train_dataset=data, peft_config=peft, **want)
    trainer.setup_data()
    trainer.setup_trainer()
    args = trainer.trainer.args
    missing = {k: (v, getattr(args, k, "ABSENT")) for k, v in want.items()
               if k not in ("report_to",) and getattr(args, k, "ABSENT") != v}
    if missing:
        raise RuntimeError(f"settings did not reach GRPOConfig: {missing}")
    print(json.dumps({"states": len(kept), "control": a.control, "config_verified": True}), flush=True)
    trainer.trainer.train()
    trainer.trainer.save_model(a.output)
    tok.save_pretrained(a.output)
    hist = trainer.trainer.state.log_history
    Path(a.output, "train_log.json").write_text(json.dumps({"states": len(kept), "control": a.control, "log_history": hist}, indent=1, default=str))
    rew = [h.get("reward") for h in hist if "reward" in h]
    print(json.dumps({"reward_first": rew[:5], "reward_last": rew[-5:]}))


if __name__ == "__main__":
    main()
