# Verification Layer Experiments — Findings Report

**Date:** September 2026
**Model:** Qwen3-4B (base, non-fine-tuned), 4-bit quantization
**Retrieval backbone:** `paraphrase-multilingual-mpnet-base-v2` embeddings over YFK (Yüksek Fen Kurulu) opinion corpus
**Goal:** Test the feasibility of a lightweight, rule-based + embedding-based verification layer on top of an existing RAG pipeline (`retrieve.py`, `rag_generate.py`), addressing advisor-recommended architecture (classifier → retrieval → generation → **verification**).

---

## 1. Motivation

A base RAG pipeline was already operational (category-filtered retrieval + Qwen3-4B generation over YFK precedents). However, no mechanism existed to verify that generated legal reasoning was actually grounded in the retrieved evidence, nor to detect when retrieved precedents disagreed with one another. This experiment series implements and empirically tests three verification components:

1. **Evidence-binding check** — sentence-level semantic similarity between generated output and retrieved source text
2. **Citation verification** — regex-based extraction and cross-checking of decision-number references (`Görüş No`, format `YYYY/NN`)
3. **Conflict detection** — comparison of outcome direction (`Karar Yönü`) across retrieved precedents

## 2. Scripts (in order of execution)

| File | Purpose |
|---|---|
| `01_prototype_verification_layer.py` | Standalone prototype using synthetic example text — validates core logic |
| `02_explore_metadata.py` | Inspects real metadata schema returned by `retrieve()` |
| `03_integration_conflict_detection.py` | First real-data test — conflict detection alone (no generation required) |
| `04_end_to_end_test.py` | First full pipeline run: real `generate_answer()` output passed through all 3 verification components |
| `05_thinking_mode_ablation.py` | Compares `enable_thinking=True` vs `False` (512 vs 1500 tokens) |
| `06_conflict_prompt_ablation.py` | Isolates length-vs-thinking effect; tests a single added instruction for explicit conflict acknowledgment |

## 3. Key Findings

### 3.1 Prototype validation (synthetic data)
The verification layer correctly identified a fabricated citation number (a decision reference not present in the source text) and an unsupported factual claim, confirming the core detection logic works before testing on live model output.

### 3.2 Real conflict detection (no generation needed)
For the query *"Süre uzatımı talebinin geç değerlendirilmesi nedeniyle uğranılan zarar"* (damage from delayed evaluation of an extension-of-time request), the top-3 retrieved YFK precedents contained a genuine outcome conflict:

| Görüş No | Similarity | Outcome |
|---|---|---|
| 2015/07 | 0.637 | Contractor-favorable |
| 2012/43 | 0.587 | Contractor-favorable |
| 2021/42 | 0.572 | **Administration-favorable** |

A naive top-1 RAG system would likely have surfaced only the highest-similarity precedent, silently suppressing the conflicting result — of particular concern since the underlying `Karar Yönü` labels are themselves marked by the research team as "rough estimates requiring verification."

### 3.3 Generation configuration ablation (4 scenarios, same query)

| Scenario | Thinking | Max Tokens | Time (s) | Unsupported Sentences | Explicit Conflict Acknowledgment |
|---|---|---|---|---|---|
| A | Off | 512 | 75.3 | 0/8 (0%) | No |
| B | On | 1500 | 195.2 | 5/44 (11.4%) | No |
| C | Off | 1500 | 131.7 | 4/18 (22.2%) | No |
| **D** | **Off** | **512** | **77.2** | **0/7 (0%)** | **Yes** |

**Critical control result:** Scenario C isolates output length from "thinking mode" as the driver of evidence-grounding degradation. Since C (thinking off, forced to 1500 tokens) showed *worse* grounding (22.2% unsupported) than B (thinking on, 11.4%), the degradation is attributable primarily to **forced output length**, not to chain-of-thought reasoning itself.

**Best configuration (D):** Adding a single sentence to the prompt — *"If precedents conflict in outcome direction, explicitly state this at the start of your response"* — was sufficient to elicit correct conflict-aware behavior, with **no measurable cost** to speed or evidence fidelity (matching the fastest, cleanest baseline).

### 3.4 Citation fidelity across all scenarios
Across all four generation configurations, **zero fabricated `Görüş No` citations** were observed (0/5, 0/5, 0/5, 0/3). The prompt-level instruction against inventing case numbers ("uydurma kanun/karar numarası verme") appears effective for this query, at least in this single-query test.

### 3.5 Verifier limitation identified and corrected
The initial evidence-binding check flagged meta-commentary sentences (e.g., "Okay, let's tackle this query," present during `thinking=True` runs) as "unsupported," conflating reasoning narration with substantive factual claims. A regex-based meta-commentary filter was added in later scripts to address this.

## 4. Recommended Production Configuration

Based on this ablation: **`enable_thinking=False`, `max_new_tokens=512`, with an explicit conflict-acknowledgment instruction appended to the prompt.**

## 5. Limitations of This Experiment Series

- **Single query tested** — all ablations used one representative delay-claim query; results should be validated across a larger, stratified sample of queries before drawing general conclusions.
- **Embedding-based evidence binding is a proxy, not ground truth** — semantic similarity thresholds (0.55/0.40) were chosen heuristically, not calibrated against human judgments of "true" grounding.
- **Citation verification only covers the `Görüş No` format** — does not yet verify substantive claims about what a cited decision *says*, only whether the citation number itself exists among retrieved sources.
- **No comparison against a non-verified baseline's downstream impact** — i.e., this study does not yet quantify how often an *unverified* system would have produced a misleading confident answer that the verification layer successfully flagged, across many queries (only demonstrated for this one case).

## 6. Next Steps

1. Repeat this ablation across a stratified sample of ~20-30 queries spanning multiple claim categories (not just "Süre Uzatımı / Gecikme")
2. Extend citation verification to check substantive alignment (not just citation existence) using the evidence-binding mechanism
3. Formalize similarity thresholds via a small human-annotated validation set
4. Integrate the conflict-acknowledgment instruction as a permanent, default component of `build_prompt()` in the production pipeline
