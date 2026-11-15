"""Batched generation backends for chat messages: vLLM (GPU, LoRA) or transformers (CPU tests / fallback)."""


class VLLMGenerator:
    def __init__(self, model, adapter=None, max_model_len=8192, max_tokens=640, temperature=0.0, gpu_mem=0.85):
        from vllm import LLM, SamplingParams
        from vllm.lora.request import LoRARequest
        import torch
        dtype = "bfloat16" if torch.cuda.get_device_capability()[0] >= 8 else "half"  # T4 (sm75): fp16
        self.llm = LLM(model=model, max_model_len=max_model_len, enable_lora=adapter is not None,
                       max_lora_rank=64, gpu_memory_utilization=gpu_mem, dtype=dtype, enforce_eager=False)
        self.params = SamplingParams(temperature=temperature, max_tokens=max_tokens)
        self.lora = LoRARequest("adapter", 1, adapter) if adapter else None
        self.tokenizer = self.llm.get_tokenizer()

    def __call__(self, batch_messages):
        outs = self.llm.chat(batch_messages, self.params, lora_request=self.lora, use_tqdm=False)
        return [o.outputs[0].text.strip() for o in outs]


def json_closed(text):
    """True once the first top-level JSON object in text has closed (string- and escape-aware)."""
    depth, in_str, esc, started = 0, False, False, False
    for ch in text:
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
            continue
        if ch == '"' and started: in_str = True
        elif ch == "{": depth += 1; started = True
        elif ch == "}" and started:
            depth -= 1
            if depth == 0:
                return True
    return False


class HFGenerator:
    """Hardened transformers generation for small GPUs: length-sorted chunks under a token budget; on CUDA OOM the
    chunk is halved and retried down to batch 1 (OOM becomes a slowdown, not a failure).
    T4 (sm75) has no native bf16 -- torch emulates it ~10x slower -- so bf16 is used only on sm80+, else fp16.
    Each sequence stops as soon as its first JSON object closes (the action parser reads only that object)."""
    def __init__(self, model, adapter=None, max_tokens=400, temperature=0.0, device=None, token_budget=24000):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(adapter or model) if adapter else AutoTokenizer.from_pretrained(model)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        if self.device == "cuda":
            dtype = torch.bfloat16 if torch.cuda.get_device_capability()[0] >= 8 else torch.float16
        else:
            dtype = torch.float32
        self.dtype = str(dtype).replace("torch.", "")
        self.model = AutoModelForCausalLM.from_pretrained(model, dtype=dtype, attn_implementation="sdpa").to(self.device)
        if adapter:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter)
        self.model.eval()
        self.max_tokens, self.temperature, self.token_budget = max_tokens, temperature, token_budget
        self.oom_retries = 0
        self.peak_gb = 0.0
        self.calls, self.gen_seconds, self.new_tokens = 0, 0.0, 0

    def _stopper(self, n_prompt, batch):
        import transformers
        tok, torch = self.tok, self.torch
        class JsonStop(transformers.StoppingCriteria):
            def __call__(self, input_ids, scores, **kw):
                return torch.tensor([json_closed(tok.decode(row[n_prompt:], skip_special_tokens=True)) for row in input_ids],
                                    device=input_ids.device, dtype=torch.bool)
        return transformers.StoppingCriteriaList([JsonStop()])

    def _generate(self, texts):
        import time
        enc = self.tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(self.device)
        n = enc["input_ids"].shape[1]
        t = time.time()
        with self.torch.inference_mode():
            out = self.model.generate(**enc, max_new_tokens=self.max_tokens, do_sample=self.temperature > 0,
                                      temperature=self.temperature or None, pad_token_id=self.tok.pad_token_id,
                                      stopping_criteria=self._stopper(n, len(texts)))
        self.gen_seconds += time.time() - t; self.calls += 1
        res = []
        for o in out:
            new = o[n:]
            self.new_tokens += int((new != self.tok.pad_token_id).sum())
            res.append(self.tok.decode(new, skip_special_tokens=True).strip())
        if self.device == "cuda":
            self.peak_gb = max(self.peak_gb, self.torch.cuda.max_memory_allocated() / 2**30)
        return res

    def _safe(self, texts):
        try:
            return self._generate(texts)
        except self.torch.cuda.OutOfMemoryError:
            self.torch.cuda.empty_cache(); self.oom_retries += 1
            if len(texts) == 1:
                raise
            h = len(texts) // 2
            return self._safe(texts[:h]) + self._safe(texts[h:])

    def __call__(self, batch_messages):
        texts = [self.tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in batch_messages]
        lens = [len(self.tok(t, add_special_tokens=False)["input_ids"]) for t in texts]
        order = sorted(range(len(texts)), key=lambda i: lens[i])
        results, chunk = [None] * len(texts), []
        def flush(idx):
            for i, r in zip(idx, self._safe([texts[i] for i in idx])):
                results[i] = r
        for i in order:
            if chunk and (len(chunk) + 1) * (lens[i] + self.max_tokens) > self.token_budget:
                flush(chunk); chunk = []
            chunk.append(i)
        if chunk:
            flush(chunk)
        return results


def make_generator(backend, model, adapter=None, **kw):
    return (VLLMGenerator if backend == "vllm" else HFGenerator)(model, adapter=adapter, **kw)
