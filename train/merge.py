"""Merge a LoRA adapter into its base model (used to start GRPO from the SFT policy)."""
import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True); p.add_argument("--adapter", required=True); p.add_argument("--output", required=True)
    a = p.parse_args()
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dtype = torch.float16
    model = AutoModelForCausalLM.from_pretrained(a.base, dtype=dtype)
    model = PeftModel.from_pretrained(model, a.adapter).merge_and_unload()
    model.save_pretrained(a.output)
    AutoTokenizer.from_pretrained(a.adapter).save_pretrained(a.output)
    print("merged ->", a.output)


if __name__ == "__main__":
    main()
