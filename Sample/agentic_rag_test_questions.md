# Agentic RAG Research Copilot Test Questions

This file contains test questions for the Northstar Benefits Group / Polaris Claims Hub synthetic document corpus.

Use these questions to evaluate whether a RAG system can:
- retrieve facts from the correct documents,
- synthesize across multiple documents,
- identify ambiguity or inconsistency,
- cite supporting evidence,
- avoid hallucinating when the corpus does not contain an answer.

---

## Answerable Questions

### 1. What is Project Meridian, and what does it not do?

**Expected answer:**  
Project Meridian is a modernization initiative for Polaris Claims Hub. It introduces a claim workspace with evidence status, eligibility status, checklist requirements, decision history, audit capture, recommendations, and carrier sync visibility. It is meant to improve claim handling, auditability, and Support explanations.

It does not replace carrier adjudication engines, make final medical necessity decisions, automate claim denials, generate explanations for employees, or change contractual plan terms or SLAs.

**Expected cited documents:**  
- `01_project_meridian_prd.md`
- PRD PDF, if included
- `09_support_kb_meridian.md`

---

### 2. Why was the original April 2026 launch plan delayed or changed?

**Expected answer:**  
The original plan was a single large April 2026 launch. It changed after the January 22, 2026 intake-classification incident, which caused unclassified evidence routing, duplicate missing-information requests, and claim status confusion. Security also requested additional event tracing.

The revised approach uses a phased rollout: read-only workspace first, then limited write actions, then carrier visibility and broader expansion.

**Expected cited documents:**  
- `01_project_meridian_prd.md`
- `05_incident_postmortem_intake_classifier.md`
- incident postmortem PDF, if included
- `10_project_meridian_roadmap.md`
- `07_decision_log_meridian.md`

---

### 3. Which teams are responsible for Support, Security, and Platform Engineering tasks across Meridian?

**Expected answer:**  
Support Operations owns training, customer-safe language, escalation routing, KB updates, and feedback collection. Support should not expose internal classifier, recommendation, audit-hold, or PHI details.

Security and Compliance own access review, broker PHI feature flag approval, policy interpretation, audit export approval, retention/privacy concerns, and incident reporting obligations.

Platform Engineering owns Workspace API, Checklist and Recommendation Service, event publisher migration, duplicate request suppression, UI integration, and technical fixes such as checklist mismatches or duplicate request defects.

**Expected cited documents:**  
- `10_project_meridian_roadmap.md`
- `09_support_kb_meridian.md`
- `08_customer_onboarding_guide.md`
- `02_meridian_architecture_design.md`

---

### 4. What is the retention period for claim records and evidence, and is there any conflict across documents?

**Expected answer:**  
The policy is seven years after claim closure, unless a customer contract or legal hold requires longer retention.

The Compliance Handbook defines the policy. The PRD says claim records, evidence metadata, and uploaded evidence files for regulated lines are retained for seven years after closure. The Architecture Design mentions seven years plus 30 days, but the PRD and Roadmap explain that this is an implementation buffer for asynchronous deletion queues, not a separate policy.

There is an unresolved ambiguity about whether the seven-year period starts at claim closure or final carrier decision for claims closed internally before carrier response.

**Expected cited documents:**  
- `04_compliance_security_handbook.md`
- compliance handbook PDF, if included
- `01_project_meridian_prd.md`
- `02_meridian_architecture_design.md`
- `10_project_meridian_roadmap.md`

---

### 5. Can brokers view medical evidence in Meridian?

**Expected answer:**  
By default, brokers cannot view uploaded medical evidence or restricted PHI. Broker users can see approved operational status fields.

Broker PHI access requires a signed broker PHI access addendum and Northstar Security approval. It is enabled through the `broker-phi-view` feature flag. Corvus BioSystems has chosen not to enable broker PHI access during the pilot.

**Expected cited documents:**  
- `01_project_meridian_prd.md`
- `08_customer_onboarding_guide.md`
- `09_support_kb_meridian.md`
- `04_compliance_security_handbook.md`

---

### 6. What customer groups are included in the Meridian pilot, and what is the rollout sequence?

**Expected answer:**  
The pilot includes Ashvale Manufacturing, BluePeak Retail Group, and Corvus BioSystems.

The rollout is phased. The revised roadmap separates read-only workspace, limited write actions, carrier sync visibility, and legacy queue retirement instead of launching everything at once in April.

The customer onboarding guide says pilot feedback and expansion decisions were expected around May 2026, but dates may shift if security review, audit validation, or tenant-specific configuration is incomplete.

**Expected cited documents:**  
- `08_customer_onboarding_guide.md`
- `09_support_kb_meridian.md`
- `10_project_meridian_roadmap.md`

---

### 7. What should Support say if a broker asks why a claim is delayed?

**Expected answer:**  
Support should use customer-safe status language and avoid internal details. They may explain approved public statuses such as “pending information,” “under review,” “sent to carrier,” or “decision received.”

Support should not mention internal audit hold, classifier regression, model confidence, or restricted evidence details. If the broker lacks PHI access, Support should avoid describing medical documents beyond safe labels such as “provider statement received,” if enabled.

**Expected cited documents:**  
- `09_support_kb_meridian.md`
- `08_customer_onboarding_guide.md`
- `01_project_meridian_prd.md`

---

### 8. What happened in the January intake-classifier incident, and what changed afterward?

**Expected answer:**  
The January 22, 2026 incident involved the intake classifier and caused evidence routing problems, duplicate missing-information requests, and confusion about claim status.

Afterward, Meridian’s launch plan changed from a big-bang launch to a phased rollout. Duplicate request suppression became an explicit validation item, and the team added stronger audit/event tracing requirements and fail-closed behavior for claim-changing actions.

**Expected cited documents:**  
- `05_incident_postmortem_intake_classifier.md`
- incident postmortem PDF, if included
- `10_project_meridian_roadmap.md`
- `07_decision_log_meridian.md`
- `03_operations_runbook_meridian.md`

---

### 9. What terminology should the app use: “case,” “packet,” or “claim”?

**Expected answer:**  
The preferred Meridian product language is “claim.”

Older LumenBridge and customer materials may use “case,” “matter,” or “packet.” Product and Platform agreed to standardize around “claim” while keeping import aliases for legacy customers. “Packet” should become “claim evidence package,” and Product asked Support Operations to retire “case” from Support macros by the end of Q2 2026.

**Expected cited documents:**  
- `01_project_meridian_prd.md`
- `07_decision_log_meridian.md`
- `10_project_meridian_roadmap.md`
- `09_support_kb_meridian.md`

---

### 10. Should reopened claims preserve the original SLA timer or start a new internal review timer?

**Expected answer:**  
The uploaded documents do not provide a final answer.

The PRD lists this as an open question, and the decision log says there is no final decision. Operations wants a new internal SLA timer after reopen, while Compliance says retention should be based on final closure.

Support is instructed not to state an undocumented policy and should only say that the claim has been reopened and is being reviewed under the current workflow.

**Expected cited documents:**  
- `01_project_meridian_prd.md`
- `07_decision_log_meridian.md`
- `09_support_kb_meridian.md`

---

## Negative-Control Questions

These questions are intentionally designed so the RAG system should **not** find a complete answer in the uploaded documents. A good answer should say that the documents do not contain enough evidence, rather than inventing information.

---

### 11. What is the exact annual contract value of the Ashvale Manufacturing account?

**Expected answer:**  
The documents may mention Ashvale Manufacturing as a pilot customer, but they should not provide an exact annual contract value. The RAG system should say that the uploaded documents do not contain the requested financial figure.

**Good behavior:**  
- Say the corpus does not provide the exact ACV.
- Cite any document that merely identifies Ashvale as a pilot customer.
- Do not invent a dollar amount.

---

### 12. What are the names and direct phone numbers of the Ashvale, BluePeak, and Corvus executive sponsors?

**Expected answer:**  
The documents may include fictional company or stakeholder names, but they should not provide direct phone numbers or complete executive sponsor contact details. The RAG system should say this information is not available in the uploaded documents.

**Good behavior:**  
- Do not fabricate names or phone numbers.
- Mention that no direct phone numbers are provided.
- Cite onboarding or QBR materials only if they contain partial customer context.

---

### 13. Which cloud region and exact database instance type does Meridian use in production?

**Expected answer:**  
The architecture document may discuss services, event publishing, APIs, or storage patterns, but the corpus should not provide exact production cloud region plus database instance type. The RAG system should say the documents do not contain enough detail to answer.

**Good behavior:**  
- Distinguish between general architecture and exact infrastructure configuration.
- Do not guess AWS/GCP/Azure region names or database SKUs.
- Cite the architecture document if it contains only partial infrastructure context.

---

### 14. What is the complete source code implementation of the Recommendation Service scoring algorithm?

**Expected answer:**  
The documents may describe recommendation behavior, requirements, or safety constraints, but they should not include complete source code for the scoring algorithm. The RAG system should say the implementation code is not included in the uploaded files.

**Good behavior:**  
- Summarize any high-level design details if available.
- Clearly state that source code is absent.
- Avoid generating code as though it came from the documents.

---

### 15. Did Northstar Benefits Group sign a final enterprise-wide rollout contract with Corvus BioSystems after the pilot?

**Expected answer:**  
The documents may mention Corvus BioSystems as a pilot customer and may discuss future expansion, but they should not confirm a final enterprise-wide rollout contract after the pilot. The RAG system should say the uploaded documents do not provide evidence of a signed final rollout contract.

**Good behavior:**  
- Say the evidence supports pilot participation only.
- Do not infer final contract signature from pilot participation.
- Cite the onboarding guide or roadmap only for pilot context.

---

### 16. What was the final legal opinion from outside counsel on reopened-claim SLA treatment?

**Expected answer:**  
The documents identify reopened-claim SLA treatment as unresolved or under discussion. They should not provide a final outside counsel legal opinion. The RAG system should state that no final legal opinion is included.

**Good behavior:**  
- Mention that the issue appears unresolved.
- Cite the PRD or decision log if they mark the topic as open.
- Do not invent legal analysis.

---

### 17. What is the password, API token, or shared secret used by Meridian to connect with carrier systems?

**Expected answer:**  
The uploaded documents should not contain passwords, API tokens, or shared secrets. The RAG system should refuse to provide credentials and state that no such credential appears in the corpus.

**Good behavior:**  
- Do not output or invent credentials.
- State that secrets are not present.
- Optionally mention that production systems should use secure secret management.

---

### 18. How many employees work at Northstar Benefits Group?

**Expected answer:**  
The corpus may describe teams and roles, but it should not provide a total company headcount. The RAG system should say the uploaded documents do not contain the total employee count.

**Good behavior:**  
- Do not estimate from team names.
- Cite no source unless a document contains partial organizational context.
- Clearly say the answer is not in the uploaded documents.

---

## Scoring Notes

Use the following criteria when evaluating the RAG application:

1. **Citation quality**  
   The answer should cite the documents that actually support the claim.

2. **Grounding**  
   The answer should use only facts present in the uploaded corpus.

3. **Cross-document synthesis**  
   For questions involving rollout, retention, roles, or incident changes, the answer should combine evidence across multiple documents.

4. **Conflict handling**  
   The answer should identify apparent inconsistencies, such as “seven years” versus “seven years plus 30 days,” and explain whether the conflict is real or merely implementation detail.

5. **Ambiguity handling**  
   For reopened-claim SLA treatment, the answer should say the issue is unresolved.

6. **Negative-control behavior**  
   For questions 11–18, the answer should not hallucinate missing facts. It should say the uploaded documents do not contain enough evidence.
