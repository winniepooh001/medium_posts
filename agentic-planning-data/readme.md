# Agentic Planning Comparison Data

Supporting data for the Medium series "Where Agentic Planning Breaks."

## Contents

- `react_prompt.md` — The 518-line system prompt used for all runs. Defines 18 analytical operations, nesting rules, discovery tool usage, and anti-patterns.
- `questions.json` — 64 questions used in the experiment, with metadata (ticker, thesis, analytical patterns, nesting depth, answerability classification).
- `hard_21.json` — 21 stratified hard questions covering depth 1-4 and all major analytical patterns.
- `execution_comparison.json` — Step-by-step execution results comparing two pipeline approaches on 16 questions.
- `runs/` — Raw plan output from each model:
  - `gemini-3.1-pro/` — 48 runs
  - `gpt-5.4/` — 22 runs
  - `deepseek-reasoner/` — 21 runs

## Run Format

Each JSON file in `runs/` contains:

```json
{
  "question_id": "Q0001",
  "plan": {
    "steps": [
      {
        "step_id": "s1",
        "operation": "fetch",
        "description": "...",
        "inputs": [],
        "params": {}
      }
    ]
  },
  "trace": [
    {"tool": "search_non_macro_catalog", "args": {}, "result": "..."}
  ],
  "duration_seconds": 18.3,
  "error": null
}
```

- `plan` — The structured HypothesisPlan emitted by the agent (null if planning failed)
- `trace` — Every discovery tool call and its result
- `duration_seconds` — Wall clock time for the full agentic loop
- `error` — Error message if the agent failed to produce a plan

## Models

| Model | Runs | Success Rate | Avg Duration |
|---|---|---|---|
| Gemini 3.1 Pro | 48 | 90% | 63s |
| GPT-5.4 | 22 | 100% | 18.5s |
| deepseek-reasoner | 21 | 29% | 196s |

## Question Complexity

Questions are stratified by nesting depth (1-4) and analytical pattern:

- **Depth 1:** Single-operation (snapshot, simple trend)
- **Depth 2:** Two-step decomposition (derived metric + trend, peer comparison)
- **Depth 3:** Multi-step chains (correlate + trend + assess, conditional comparisons)
- **Depth 4:** Complex chains (sensitivity analysis, multi-factor attribution)

Analytical patterns: TREND, CORRELATE, PEER, DERIVED, THRESHOLD, NARRATIVE, CHAIN, SUBPLAN, SNAPSHOT, GROWTH, PROXY.
