"""Batched generation backends for chat messages: vLLM (GPU, LoRA) or transformers (CPU tests / fallback)."""


class VLLMGenerator:
    def __init__(self, model, adapter=None, max_model_len=8192, max_tokens=640, temperature=0.0, gpu_mem=0.85):
        from vllm import LLM, SamplingParams
        from vllm.lora.request import LoRARequest
        self.llm = LLM(model=model, max_model_len=max_model_len, enable_lora=adapter is not None,
                       max_lora_rank=64, gpu_memory_utilization=gpu_mem, dtype="bfloat16")
        self.params = SamplingParams(temperature=temperature, max_tokens=max_tokens)
        self.lora = LoRARequest("adapter", 1, adapter) if adapter else None
        self.tokenizer = self.llm.get_tokenizer()

    def __call__(self, batch_messages):
        outs = self.llm.chat(batch_messages, self.params, lora_request=self.lora, use_tqdm=False)
        return [o.outputs[0].text.strip() for o in outs]


class HFGenerator:
    def __init__(self, model, adapter=None, max_tokens=640, temperature=0.0, device=None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(model)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        dtype = (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16) if self.device == "cuda" else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(model, dtype=dtype).to(self.device)
        if adapter:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter)
        self.model.eval()
        self.max_tokens, self.temperature = max_tokens, temperature

    def __call__(self, batch_messages, token_budget=40000):
        texts = [self.tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in batch_messages]
        lens = [len(self.tok(t, add_special_tokens=False)["input_ids"]) for t in texts]
        order = sorted(range(len(texts)), key=lambda i: lens[i])
        results, chunk = [None] * len(texts), []
        def flush(idx):
            enc = self.tok([texts[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to(self.device)
            with self.torch.no_grad():
                out = self.model.generate(**enc, max_new_tokens=self.max_tokens, do_sample=self.temperature > 0,
                                          temperature=self.temperature or None, pad_token_id=self.tok.pad_token_id)
            for i, o in zip(idx, out):
                results[i] = self.tok.decode(o[enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        for i in order:  # length-sorted chunks under a token budget (prompt + generation) to fit a 16 GB T4
            if chunk and (len(chunk) + 1) * (lens[i] + self.max_tokens) > token_budget:
                flush(chunk); chunk = []
            chunk.append(i)
        if chunk:
            flush(chunk)
        return results


def make_generator(backend, model, adapter=None, **kw):
    return (VLLMGenerator if backend == "vllm" else HFGenerator)(model, adapter=adapter, **kw)
