# Conversational AI Failure Taxonomy & Regression Testing Strategies

AgentAssure standardizes conversational failure diagnosis into a rigorous **7+3 Taxonomy** (7 Core conversational failure modes + 3 Multimodal/Vernacular edge failure modes). Every confirmed failure is mapped directly to deterministic and semantic assertion strategies in the regression test harness.

---

## 1. Core Conversational Failure Modes (7 Categories)

### 1. Factual Accuracy & Hallucination
* **Definition**: The agent invents interest rates, repayment tenures, product features, or policy terms absent from canonical knowledge bases.
* **Severity**: `S1 (Critical)` or `S2 (Major)`.
* **Root Causes**: Unconstrained temperature (>0.3), ambiguous retrieval context, or weak negative instruction prompts.
* **Regression Test Strategy**:
  - `no_hallucination` assertion rule passing unsupported terms list.
  - Semantic cross-encoder similarity check against ground-truth KB chunk.
  - Strict numerical range assertion (e.g., `10.25% <= rate <= 14.5%`).

### 2. Regulatory & Compliance Breach
* **Definition**: Failure to state statutory RBI or banking disclaimers, giving unauthorized financial investment advice, or violating privacy policies.
* **Severity**: `S1 (Critical)` - Release Blocker.
* **Root Causes**: Prompt truncation, instruction drift, or user conversational deflection.
* **Regression Test Strategy**:
  - `compliance_check` assertion verifying mandatory statutory tokens (e.g. `"terms and conditions apply"`).
  - Negative regex assertions forbidding unauthorized assurances (e.g., `"guaranteed return"`, `"100% approval"`).

### 3. Prompt Injection & Security Vulnerability
* **Definition**: Susceptibility to jailbreaks, developer mode overrides, system prompt extraction, or API token exposure.
* **Severity**: `S1 (Critical)` - Release Blocker.
* **Root Causes**: Inadequate adversarial red-teaming and missing boundary guardrails.
* **Regression Test Strategy**:
  - `must_not_contain` assertion scanning for internal prompt instructions, model names, or secret keys.
  - Multi-turn adversarial jailbreak persona simulation.

### 4. Knowledge Base Misretrieval
* **Definition**: Downstream retrieval-augmented generation (RAG) fetches irrelevant, outdated, or conflicting document chunks.
* **Severity**: `S2 (Major)` or `S3 (Moderate)`.
* **Root Causes**: Vector index drift, improper chunk size/overlap, or lack of reranking.
* **Regression Test Strategy**:
  - Chunk ID provenance assertions verifying the expected source document was retrieved.
  - Synthetic RAG test harness injecting counterfactual queries.

### 5. Entity Extraction & Slot Filling Error
* **Definition**: Incorrect parsing of customer dates, account numbers, amounts, or customer intents.
* **Severity**: `S2 (Major)`.
* **Root Causes**: Formatting variance, phonetic confusion, or complex sentence syntax.
* **Regression Test Strategy**:
  - JSON schema parameter validation on tool call invocations.
  - Regular expression assertions on extracted slot values.

### 6. Tone, Sentiment & Empathy Failure
* **Definition**: Defensive demeanor, robotic indifference during customer financial escalation, or sarcasm.
* **Severity**: `S3 (Moderate)` or `S4 (Minor)`.
* **Root Causes**: Overly rigid system prompt guidelines, lack of emotional intelligence calibration.
* **Regression Test Strategy**:
  - Valence sentiment scoring (must maintain neutral-to-positive score > 0.6).
  - Forbidden phrasing list (e.g., `"calm down"`, `"not our problem"`).

### 7. Conversational Flow & Infinite Loops
* **Definition**: Repetitive non-progress verification cycles, circular dead-ends, or premature disconnection.
* **Severity**: `S2 (Major)`.
* **Root Causes**: Missing dialogue state transition rules or failure to recognize user has already provided requested data.
* **Regression Test Strategy**:
  - Multi-turn dialogue history tracking measuring turn-to-turn Levenshtein string similarity (flags repetition > 0.85).
  - State machine assertion verifying dialogue advances to the next step.

---

## 2. Multimodal & Vernacular Edge Modes (3 Categories)

### 8. Linguistic Robustness (Code-Switching & Hinglish)
* **Definition**: Inability to parse mixed Hindi-English colloquialisms (*"Mera auto-debit bounce ho gaya yaar"*).
* **Severity**: `S2 (Major)` or `S3 (Moderate)`.
* **Root Causes**: English-centric LLM tokenizer and lack of bilingual colloquial fine-tuning.
* **Regression Test Strategy**:
  - Dual-language test suite containing real customer Hinglish transcripts.
  - Semantic intent preservation check regardless of transliterated phrasing.

### 9. Conversational Dynamics & Interruption (Barge-in)
* **Definition**: Disorientation or dialogue stall when customer interrupts mid-utterance.
* **Severity**: `S3 (Moderate)`.
* **Root Causes**: Full-duplex audio state machine latency or lack of turn cancellation tokens.
* **Regression Test Strategy**:
  - Latency SLA assertion (`latency_under <= 1200ms` for audio cancellation).
  - Truncated prompt evaluation asserting agent immediately addresses interruption topic.

### 10. Audio & ASR Quality Degradation
* **Definition**: Acoustic misrecognition of domain terminology and phonetic homophones (*"into rest"* vs. *"interest"*).
* **Severity**: `S3 (Moderate)` or `S4 (Minor)`.
* **Root Causes**: Acoustic distortion, low bitrate telephone audio, or regional accent mismatch.
* **Regression Test Strategy**:
  - Acoustic Word Error Rate (WER) degradation simulation.
  - Vocabulary boost list assertion verifying proper noun phonetic handling.

---

## 3. Taxonomy to Assertion Mapping Matrix

| Category | Primary Metric | Assertion Type | Gate Threshold |
| :--- | :--- | :--- | :--- |
| **Factual Accuracy** | Hallucination Rate | `no_hallucination`, `must_contain` | **&ge; 95%** |
| **Compliance** | Statutory Inclusion | `compliance_check` | **&ge; 95%** |
| **Prompt Injection** | Attack Surface | `must_not_contain` | **&ge; 95%** |
| **KB Retrieval** | Chunk Recall | `must_contain`, `json_schema` | &ge; 88% |
| **Understanding** | Slot Accuracy | `regex_match` | &ge; 90% |
| **Experience** | Sentiment Score | `must_not_contain` | &ge; 85% |
| **Conversational Flow** | Loop Count | `latency_under`, `repetition_check` | &ge; 90% |
| **Hinglish Robustness** | Bilingual Intent | `must_contain` | &ge; 88% |
| **Dynamics** | Barge-in SLA | `latency_under` | &ge; 85% |
| **Audio / ASR** | WER Tolerance | `regex_match` | &ge; 88% |
