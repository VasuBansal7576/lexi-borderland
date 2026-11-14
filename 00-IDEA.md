# The idea (what you wanted)

## Your idea, in your words
Alice in Borderland turned into an RL world: "like alice in borderland games converted into a world with rooms etc like that."

- "no watering down anything, need to create the best env"
- A game-room setup, level by level, where "none of the levels are easy", testing memory, long context and more.
- Your spec (10/25): one causal world, not seven separate games. Sample one hidden set of facts per episode. Each room reveals some evidence about it, and later right moves depend on earlier facts. A perfect-information solver must succeed; a memoryless solver must provably fall short.
- Counterfactual twins: worlds that differ in one fact must change the right answers downstream.
- Headline metric: dependency exploitation, measured against four ceilings (oracle, memoryless, scripted heuristic, random).
- Failure attribution for every miss: fact never discovered, discovered but not recorded, or recorded but not used.
- Osmosis as the convergence room where everything learned comes together.
- A genuinely good env for small open-weight models, fast, and proven end to end: it has to actually make a model better, not just be hard.

## The Lexsi version (Lexsi AI Safety & Alignment Hackathon, Track 3: Agentic Fine-tuning)
Same idea, built fresh on Lexsi's stack:
- Train Cohere Tiny Aya with Lexsi's AgentTune (GRPO) on a 7-room causal Borderland world.
- Facts found early decide answers later. After room 3 the agent's memory is wiped (sealed); only an 8-line notebook survives.
- Every solved room pays (dense mid-task reward), not 0 until full escape.
- Two trap tools that "work" but zero the episode, to measure cheating.
- Grade before vs after with Lexsi's AuditKIT on held-out seeds, against a random-reward control, with outputs read by eye for reward hacks.
- Success = a real held-out improvement from GRPO after an SFT warm start. SFT alone doesn't count. Video only after real logs.
- Dates: submit Nov 14, top 20 on Nov 16, demo day Nov 22.

## Honest status (as of Nov 7, when work stopped)
- Built: the `causalgames` environment, reward, baseline policies, AuditKIT hookup, wipe-aware AgentTune rollout, Kaggle notebook (v32), tests (18 pass).
- Best verified model result (v31): after SFT, the training probe seed scored 1.0 but the held-out seed scored 0. No verified GRPO improvement.
- The v32 Kaggle batch run failed on a missing HF_TOKEN before training; no v32 checkpoint exists.
- The CPU audit (project/audit/20261107_041436_cpu_repro/FINDINGS.md) found real bugs still unfixed: seed not reaching the rollout, warmup making lr 0 on a 1-step GRPO run, GRPO far too small, mismatched before/after eval settings, rollout tokens missing chat role tokens, and held-out seed 9000 contaminated.
- project/STATUS.md has the full log, including retractions of earlier wrong claims.

## What's in this folder
- 00-IDEA.md: this file
- project/: full code, notebooks, runs, tests, audits, STATUS.md, DESIGN.md, README.md (model weights and tokenizer copies from CPU test runs left out)
- videos/: plan explainer and build explainer (made before any real training, so not proof)
- hackathon-info/: the Lexsi hackathon page
- original-idea-sources/: your original Borderland messages and the audit of what got built against them
