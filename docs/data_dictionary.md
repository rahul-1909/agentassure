# AgentAssure Data Dictionary

This document details the complete relational schema for AgentAssure managed via SQLAlchemy 2.0 ORM.

---

## 1. `users`
Represents system actors (reviewers, managers, administrators, viewers) and handles authentication and RBAC.

| Column | Type | Nullable | Constraints / Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `username` | VARCHAR(100) | No | Unique, Indexed | Unique login handle |
| `email` | VARCHAR(255) | No | Unique, Indexed | Contact email address |
| `hashed_password` | VARCHAR(255) | No | - | Bcrypt hashed password |
| `role` | VARCHAR(50) | No | Default: `'reviewer'` | RBAC Role (`admin`, `qa_manager`, `reviewer`, `viewer`) |
| `full_name` | VARCHAR(200) | Yes | - | Display name of user |
| `is_active` | BOOLEAN | No | Default: `True` | Account operational status |
| `created_at` | TIMESTAMPTZ | No | UTC Now | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | UTC Now | Record update timestamp |

---

## 2. `audit_logs`
Immutable compliance audit trail recording all data access and actions.

| Column | Type | Nullable | Constraints / Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `user_id` | VARCHAR(36) | Yes | FK &rarr; `users.id` | User who initiated action |
| `action` | VARCHAR(100) | No | Indexed | Action verb (e.g., `submit_annotation`) |
| `entity_type` | VARCHAR(100) | No | Indexed | Affected entity name |
| `entity_id` | VARCHAR(100) | Yes | - | Identifier of target entity |
| `ip_address` | VARCHAR(45) | Yes | - | Client IPv4 or IPv6 address |
| `details` | JSON | Yes | - | Contextual metadata payload |
| `created_at` | TIMESTAMPTZ | No | UTC Now | Timestamp of audit entry |

---

## 3. `conversations`
Core entity storing voice and chat sessions along with risk telemetry signals.

| Column | Type | Nullable | Constraints / Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `customer_id` | VARCHAR(100) | No | Indexed | Masked or pseudonymized customer ID |
| `channel` | VARCHAR(20) | No | Default: `'voice'` | Channel modality (`voice`, `chat`) |
| `agent_version` | VARCHAR(50) | No | Indexed | Software release version of conversational bot |
| `duration_seconds`| FLOAT | No | Default: `0.0` | Total session duration in seconds |
| `audio_url` | VARCHAR(500) | Yes | - | S3/GCS URL to audio recording |
| `language` | VARCHAR(20) | No | Default: `'en'` | Primary session language (`en`, `hi`, `hinglish`) |
| `judge_score` | FLOAT | No | Default: `1.0`, Indexed | Automated LLM judge quality rating (0.0 to 1.0) |
| `asr_error_rate` | FLOAT | No | Default: `0.0`, Indexed | Word Error Rate (WER) proportion |
| `loop_count` | INTEGER | No | Default: `0`, Indexed | Count of detected circular repetitive turns |
| `customer_dropped`| BOOLEAN | No | Default: `False`, Indexed | True if user hung up abruptly |
| `negative_sentiment`| FLOAT | No | Default: `0.0`, Indexed | Degree of negative customer sentiment (0.0 to 1.0) |
| `risk_score` | FLOAT | No | Default: `0.0`, Indexed | Composite prioritized risk score [0.0, 1.0] |
| `sample_stratum` | VARCHAR(50) | No | Default: `'risk_ranked'` | Stratum category (`risk_ranked`, `new_version`, `edge_case`) |
| `review_status` | VARCHAR(50) | No | Default: `'pending'` | Review lifecycle status |
| `is_archived` | BOOLEAN | No | Default: `False` | 60-day archival flag |
| `is_purged` | BOOLEAN | No | Default: `False` | 90-day PII purge compliance flag |

---

## 4. `turns`
Individual conversational turns between customer, agent, or system.

| Column | Type | Nullable | Constraints / Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `conversation_id`| VARCHAR(36) | No | FK &rarr; `conversations.id` | Parent conversation |
| `turn_index` | INTEGER | No | Indexed | Order index in conversation (0, 1, 2...) |
| `speaker` | VARCHAR(20) | No | - | Speaker identity (`user`, `agent`, `system`) |
| `transcript` | TEXT | No | - | Sanitized dialogue utterance |
| `audio_start_time`| FLOAT | No | Default: `0.0` | Start offset in seconds for waveform player |
| `audio_end_time` | FLOAT | No | Default: `0.0` | End offset in seconds for waveform player |
| `asr_confidence` | FLOAT | No | Default: `1.0` | Acoustic confidence score |
| `intent` | VARCHAR(100) | Yes | - | Extracted user intent |
| `entities` | JSON | Yes | - | Extracted named entities |

---

## 5. `annotations`
Human QA review findings and defect tags.

| Column | Type | Nullable | Constraints / Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `conversation_id`| VARCHAR(36) | No | FK &rarr; `conversations.id` | Target conversation |
| `turn_id` | VARCHAR(36) | No | FK &rarr; `turns.id` | Target turn |
| `reviewer_id` | VARCHAR(36) | No | FK &rarr; `users.id` | Reviewer user |
| `failure_category_l1`| VARCHAR(100) | No | Indexed | L1 taxonomy category |
| `failure_category_l2`| VARCHAR(100) | No | Indexed | L2 specific failure subtype |
| `severity` | VARCHAR(10) | No | Default: `'S3'` | Severity classification (`S1` to `S4`) |
| `root_cause_notes`| TEXT | Yes | - | Diagnostic explanation of defect |
| `is_confirmed_failure`| BOOLEAN | No | Default: `True` | Flag indicating true positive failure |
| `fix_type` | VARCHAR(50) | No | Default: `'prompt_patch'` | Suggested remediation |
| `review_duration_seconds`| FLOAT | No | Default: `0.0` | Turnaround time spent by reviewer |
| `tags` | JSON | Yes | - | Custom searchable tags |

---

## 6. `regression_test_cases`
Distilled executable regression tests created from confirmed failures.

| Column | Type | Nullable | Constraints / Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `title` | VARCHAR(255) | No | - | Human-readable test title |
| `category_l1` | VARCHAR(100) | No | Indexed | Primary category |
| `category_l2` | VARCHAR(100) | No | Indexed | Subcategory |
| `severity` | VARCHAR(10) | No | Indexed | Defect severity |
| `language` | VARCHAR(20) | No | Default: `'en'` | Language of test case |
| `conversation_context`| JSON | No | - | Preceding dialogue turns |
| `expected_behavior`| TEXT | No | - | Target compliant agent output |
| `actual_behavior`| TEXT | No | - | Historical defect observed |
| `fix_suggestion` | TEXT | No | - | Engineering remediation advice |
| `assertion_rules`| JSON | No | Default: `[]` | List of structured assertion configurations |
| `is_active` | BOOLEAN | No | Default: `True` | Whether test is included in CI suite |
