# Project Meridian Product Requirements Document

**Filename:** 01_project_meridian_prd.md  
**Document type:** Product Requirements Document  
**Date:** 2026-02-14  
**Owner:** Priya Menon, Director of Product  
**Status:** Approved for phased rollout  
**Related documents:** 02_meridian_architecture_design.md, 07_decision_log_meridian.md, 10_project_meridian_roadmap.md

## Version History

| Version | Date | Author | Notes |
|---|---:|---|---|
| 0.6 | 2025-11-18 | Priya Menon | Initial draft based on broker advisory board feedback |
| 0.9 | 2026-01-09 | Priya Menon / Evan Cho | Added audit export and carrier synchronization requirements |
| 1.0 | 2026-02-14 | Product Council | Approved with exception for bulk evidence upload in Phase 2 |
| 1.1 | 2026-03-03 | Priya Menon | Clarified retention references and amended claims reopen flow |

## Purpose Summary

Project Meridian modernizes the intake, evidence review, and adjudication workflow in Polaris Claims Hub. The goal is to replace several ticket-style queues with a rules-guided claim workspace that provides explainable recommendations, better audit capture, and improved service-level tracking for Support and Operations.

## Background

Northstar Benefits Group has historically processed claim-related work through a combination of claim records, queue filters, manual notes, carrier portal screenshots, and separate broker escalations. The Polaris Claims Hub product grew quickly after the 2024 acquisition of LumenBridge TPA Services, and the inherited workflows still show that history. Different customers use terms such as “case,” “claim,” “matter,” “benefit event,” and “packet.” Internally, Product and Platform Engineering agreed in Decision D-014 to standardize the product language around “claim” while keeping import aliases for legacy customers.

Three customer cohorts drove the Meridian scope:

1. Employers with more than 4,000 covered lives that require predictable evidence collection.
2. Broker partners who need visibility into claim delays without seeing protected medical details.
3. Internal Operations teams that want queue metrics by plan, state, carrier, and reason code.

The original plan, circulated in Q4 2025, targeted one large launch in April 2026. That approach changed after an intake-classification incident on January 22, 2026 and after Security requested additional event tracing. The current plan is a phased rollout beginning with read-only recommendations and limited-action adjudication tools.

## Goals

Meridian must make claim handling faster, more auditable, and easier to explain without increasing compliance risk. The product goals are:

- Reduce median time from claim submission to first human review from 18.6 business hours to 8 business hours for configured customers.
- Reduce duplicate evidence requests by at least 30 percent compared with Q4 2025.
- Provide a claim workspace that shows evidence status, eligibility status, plan rules, decision history, carrier sync state, and pending customer actions in one screen.
- Capture immutable event history for claim intake, routing, document review, recommendation display, adjudicator override, and outbound carrier sync.
- Allow Support to answer “why is this claim delayed?” without exposing restricted medical evidence to broker-only users.
- Improve operational reporting by exposing queue aging, blocked reasons, and plan-specific exception counts.

## Non-Goals

Meridian is not a replacement for carrier adjudication engines. It does not make final medical necessity decisions. It does not introduce automated denial. It does not provide machine-generated explanations to employees. It does not change contractual plan terms or customer-specific service-level agreements.

The PRD explicitly excludes: automated adverse-benefit determinations, medical code interpretation, long-term disability adjudication, and direct payroll debit initiation. Payroll file export remains a separate LedgerBridge module owned by Finance Systems.

## Personas

**Operations Adjudicator:** Reviews evidence, confirms eligibility, requests missing documents, and records claim outcomes. Needs a complete view of a claim without switching between queue, document viewer, plan table, and carrier notes.

**Support Specialist:** Answers employer and broker questions about claim status. Needs safe summary fields and escalation reasons, not full medical detail.

**Customer Benefits Administrator:** Uploads evidence, monitors claim status, and responds to missing information requests. Needs clear instructions, deadline visibility, and confirmation that uploads were received.

**Security and Compliance Reviewer:** Audits access and event history. Needs evidence of who viewed or changed claim data, why recommendations were shown, and whether retention policies were followed.

**Carrier Integration Analyst:** Monitors outbound synchronization to carriers. Needs retry states, mapping errors, and plan-specific carrier identifiers.

## Scope

Meridian covers short-term disability, supplemental accident, hospital indemnity, and critical illness claims for customers using Polaris Claims Hub. Phase 1 excludes dental, vision, workers’ compensation, and long-term disability. Imported claims from the legacy LumenBridge portal are included only if they have a current claim identifier and an active employer group mapping.

## Functional Requirements

### FR-1: Unified Claim Workspace

The workspace must show claim summary, member identity, employer group, plan, benefit type, intake source, assigned queue, evidence list, pending tasks, decision history, and carrier sync state. Fields containing medical evidence details must be hidden from broker role profiles unless the customer has a signed broker PHI access addendum and the Security team has enabled the broker-phi-view feature flag.

### FR-2: Evidence Checklist

The system must generate a checklist of required evidence based on benefit type, employer group, state jurisdiction, and carrier configuration. For example, a supplemental accident claim may require an incident report, treating provider statement, employee attestation, and employer confirmation of coverage. If a customer-specific plan document overrides the default carrier checklist, the workspace must display the customer-specific requirement and record the source of the rule.

### FR-3: Recommendation Banner

The workspace may display non-binding recommendations such as “eligible for review,” “missing provider statement,” “possible duplicate claim,” or “carrier mapping error.” Recommendations must include a reason code, input facts used, and a timestamp. Recommendations must not say that a claim should be denied. The language restriction came from Compliance review on 2026-01-31.

### FR-4: Adjudicator Override

Authorized adjudicators may override a recommendation. The system must require an override reason selected from a controlled list plus optional free text. Controlled reasons include customer exception, plan document ambiguity, evidence sufficient after manual review, duplicate dismissed, carrier instruction, and other. The override event must include user ID, timestamp, prior recommendation, new status, and reason.

### FR-5: Status Model

The claim status model uses the following public statuses: received, pending information, under review, sent to carrier, decision received, closed, reopened. Internal statuses include intake_pending, classification_pending, reviewer_assigned, evidence_blocked, carrier_sync_pending, carrier_sync_failed, audit_hold, and manual_exception. Public statuses should never expose audit_hold.

### FR-6: Missing Information Requests

Adjudicators must be able to send missing information requests using approved templates. Templates may be customized by employer group but must retain required compliance language. Requests can be sent through portal notification and email. SMS is out of scope for Phase 1.

### FR-7: Audit Export

Compliance users must be able to export claim event history for a claim or batch of claims. Audit export must include event name, actor, role, timestamp, source IP when available, old value, new value, and evidence reference ID. Export format is CSV in Phase 1, with signed JSON planned for later. Export jobs must be logged as audit events themselves.

### FR-8: Carrier Synchronization Visibility

The workspace must show whether outbound carrier sync is pending, successful, failed, or manually suppressed. It must display the last attempt time, error category, retry count, and integration owner. This requirement was added after multiple brokers complained that Support could not distinguish carrier downtime from internal review delays.

### FR-9: Role-Based Views

Role profiles must be centrally managed. Product accepts the existing role model from the compliance handbook, with one addition: the Carrier Integration Analyst role can view carrier mapping metadata and sync payload status but cannot view uploaded medical evidence unless separately assigned reviewer access.

### FR-10: Reporting Events

The event stream must publish claim_received, evidence_uploaded, checklist_generated, recommendation_displayed, recommendation_overridden, missing_info_requested, claim_sent_to_carrier, carrier_sync_failed, claim_reopened, and claim_closed. These events feed Operations dashboards and quarterly business reporting.

## Data and Retention Requirements

The PRD references the retention policy in the Compliance Handbook. Claim records and evidence metadata are retained for seven years after claim closure unless a customer contract or legal hold requires a longer period. Uploaded evidence files are retained for seven years after closure for regulated lines in Phase 1. The Architecture Design notes an implementation target of seven years plus 30 days to account for asynchronous deletion queues; Product considers that an implementation buffer, not a separate policy.

Recommendation inputs and outputs must be retained with the claim event history. Temporary classification artifacts that do not become audit events should be deleted within 30 days. Security requested that raw extracted text from uploaded evidence not be persisted outside the document service, except for indexed snippets necessary for search and retrieval within the tenant boundary.

## Metrics

Primary launch metrics:
- Median time to first human review.
- Percent of claims with duplicate evidence requests.
- Percent of claims with complete event history.
- Recommendation override rate by reason code.
- Carrier sync success rate within two hours of final internal review.
- Number of Support escalations tagged “status unclear.”

Guardrail metrics:
- Unauthorized access incidents.
- Missing audit event defects.
- Increase in claim reopen rate.
- Carrier sync retries per 1,000 claims.
- Customer-reported confusion about missing information templates.

## Launch Criteria

Phase 1 requires the following:

- Successful completion of security review for workspace permissions.
- Event stream validation in staging with at least 25 synthetic claims.
- Compliance approval of recommendation wording.
- Operations training for two pilot teams.
- Customer onboarding guide updated for Meridian-specific evidence steps.
- Runbook updated with carrier sync failure process.
- No unresolved Sev-1 or Sev-2 defects.

The original launch criteria included bulk evidence upload, but that requirement moved to Phase 2 because document deduplication accuracy was below target during February testing.

## Open Questions

1. Should reopened claims preserve original SLA timers or start a new internal review timer?
2. Can Support see a checklist item label if the label implies a medical condition?
3. Should carrier sync failures be visible to employer administrators or only to internal teams?
4. Does the seven-year retention period begin at claim closure or final carrier decision for claims closed internally before a carrier response?
5. Who owns template localization for customers operating in Quebec?

## Risks

The largest product risk is that recommendations will be interpreted as automated decisions. Product mitigates this through non-binding language, explicit reason codes, and override capture. The largest operational risk is partial rollout confusion, since some customers will see Meridian workspace fields while others remain on legacy queues. The largest technical risk is event-order inconsistency between the claim service, document service, and integration service.

## Appendix A: Sample Claim Timeline

A typical claim may be received on Monday morning through the employer portal, classified as supplemental accident, assigned to Team Cedar, and flagged as missing an incident report. The adjudicator requests missing information, the customer uploads the report, and the recommendation changes to eligible for review. The adjudicator records an approval outcome and sends the claim to the carrier. Carrier sync fails once due to a mapping error and succeeds after the integration analyst corrects the carrier employer group ID. Each step must be visible in the claim event history.

## Appendix B: Terminology

The word “packet” appears in older LumenBridge documentation and customer materials. In Meridian UI, the preferred term is “claim evidence package.” The word “case” remains in a few Support macros, but Product has asked Support Operations to retire it by the end of Q2 2026.
