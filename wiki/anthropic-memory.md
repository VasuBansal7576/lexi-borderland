# Anthropic memory: what we read and what we should use

Read on 2026-11-13. Local access was restricted to this project folder; the external Desktop topic wiki was not consulted. Research used public web sources only. Nothing in this project was uploaded to a hosted memory service.

## Sources inspected

- Anthropic, [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), published November 6, 2026: full article text, experiments, caveats and outbound cookbook links.
- Official [knowledge-wiki quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/knowledge-wiki): README, the notebook's methodology and workflow code, and all four prompt files. The notebook was inspected as source/recorded output; it was not executed here. Some raw notebook formatting was altered by the page reader, so this is a design review rather than a byte-exact code audit.
- The article also links Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). The official Anthropic implementation is the primary GitHub reference for our recommendation.

## What the article establishes, and its limits

Anthropic distinguishes transcripts, selected notes, synthesized representations and a small injected index. Offline consolidation can correct notes against evidence and organize cross-document relationships. Its reported wiki-plus-search score was 61%, versus 53% for search alone, on 25 questions over a large internal corpus. Wiki-only performance reached 48%. Some single-document tasks gained little; one wiki grew larger than its inputs.

The article also describes stale game notes, model-dependent benefits from memory instructions, and lost facts when concurrent writers share a page. It argues for selective memory and maintenance, not indiscriminate storage. Those are task-specific results, not measured improvements for Codex or this project. [Article](https://www.anthropic.com/research/components-of-agent-memory)

## What the GitHub implementation actually does

The quickstart uses Markdown files with frontmatter, source references, dates, aliases and links. Its workflow extracts document batches, resolves selected gaps, checks the extraction against sources and organizes the result. Query agents mount the wiki read-only. Superseded facts retain their validity interval; incompatible metrics are kept distinct. [Notebook](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/knowledge-wiki/distill_documents_into_knowledge_wiki.ipynb)

Its reported benchmark uses 21 questions, 27 runs and two model judges. The default cost comparison changes both model and information representation; it is not an isolated same-model memory effect. Answer keys are not shipped. The notebook also reports unresolved links and acknowledges shared-page content loss. These details matter when interpreting the attractive headline. [Notebook methodology and limitations](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/knowledge-wiki/distill_documents_into_knowledge_wiki.ipynb)

The analyzer checks claims against input evidence, distinguishes observations from inferences and preserves unresolved conflicts. The organizer handles cross-file reconciliation and link repair after analysis finishes. Reading these prompts is useful even if we never use Managed Agents. [Analyzer](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/knowledge-wiki/prompts/analyzer_system.md), [organizer](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/knowledge-wiki/prompts/organizer_system.md)

## Recommendation for us

I can carry out the environment design and implementation without deploying a separate memory product. I expect a small project wiki to improve continuity as the work spans design, code, experiments and later chats. That expectation is an inference from the workflow, not a measured claim that this assistant is now more capable.

The useful information here is not a massive document corpus. It is the evolving set of constraints: which causal dependencies are intentional; why a reward formula changed; which runs actually updated weights; which seeds were inspected; and which unresolved issue still invalidates a result. A short index and a few canonical pages can preserve that without a database, embeddings, paid API pipeline or repeated autonomous consolidation jobs.

The files in this directory are that lightweight starting point. Source material remains separate from conclusions: `00-IDEA.md` is unchanged; source URLs stay attached to research; proposed mechanics are labelled proposals; actual checks have a command and result. When implementation exists, run logs and test outputs should be cited by exact local paths, not summarized into unsupported success claims.

Use targeted maintenance after meaningful changes: compare the changed page with its evidence, correct stale claims, update links and record unresolved contradictions. Do not repeatedly rewrite all pages or load them all into every prompt. A future comparison could measure factual recovery and consistency on a frozen set of project questions with and without the index, but no such experiment has been run.

## How the reading affected this environment design

These are our design choices, not claims that Anthropic evaluated our game:

| Design choice | Why it matters here | Where it is specified |
| --- | --- | --- |
| Preserve evidence separately from notes | A plausible notebook entry can be wrong; the evaluator needs the delivered source to diagnose it | [Evaluation](evaluation.md#failure-attribution-without-pretending-to-read-minds) |
| Treat facts as time-scoped | R6 introduces a real amendment and a forgery; blindly overwriting an earlier rule must fail | [Witch Hunt](rooms.md#6-witch-hunt--repair-the-model-of-the-world) |
| Let the player choose what to write | The benchmark tests selection and compression; a mandatory perfect-fact template would solve part of the task for it | [Notebook and seal](world.md#the-seal-after-room-3) |
| Keep project memory out of the player harness | Our design wiki contains private rules and evaluator knowledge | [World boundaries](world.md) |
| Do not call retrieval improvement RL improvement | Better external context and changed model weights are different interventions | [Training controls](evaluation.md#prove-post-training-improvement) |
| Audit maintenance instead of trusting prose | A memory note reporting a passed run is not a run artifact | [Verification](verification.md) |

A post-seal player wiki with unrestricted transcript retrieval would violate the original notebook challenge. We can later test alternative memory systems as explicitly separate benchmark conditions. The proposed core environment keeps the eight-line limit.
