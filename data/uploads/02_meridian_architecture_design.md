# Meridian Technical Architecture and Design

**Filename:** 02_meridian_architecture_design.md  
**Document type:** Technical Architecture / Design Document  
**Date:** 2026-02-28  
**Owner:** Evan Cho, Principal Engineer  
**Status:** Architecture Review Board accepted with conditions  
**Related documents:** 01_project_meridian_prd.md, 03_operations_runbook_meridian.md, 05_incident_postmortem_intake_classifier.md

## Purpose Summary

This document describes the technical design for Meridian’s claim workspace, recommendation service, event capture, document handling, and carrier synchronization. It is written for Platform Engineering, Security, Site Reliability Engineering, and Integration Engineering.

## Executive Summary

Meridian introduces an event-centered claim workflow layered on existing Polaris Claims Hub services. It does not replace the core Claim Service in Phase 1. Instead, it adds a Claim Workspace API, a Checklist and Recommendation Service, enhanced audit event publishing, and an integration status adapter. The architecture prioritizes traceability and tenant isolation over aggressive automation.

The central design choice is to treat recommendations as explainable workflow aids rather than decisions. The Recommendation Service emits a recommendation_displayed event only after storing the input fact references used to generate the recommendation. Adjudicator actions remain authoritative. No recommendation directly changes a public claim status.

## Current System Context

Before Meridian, the main services were:

- Claim Service: owns claim lifecycle state, internal status, public status, assignee, and basic plan metadata.
- Document Service: owns evidence file upload, malware scan status, OCR output, document type, and evidence references.
- Eligibility Service: owns member coverage windows, employment status, plan enrollment, and eligibility exceptions.
- Integration Service: handles outbound carrier payloads and retry scheduling.
- Audit Service: receives events and stores append-only audit records.
- Portal UI: used by employer administrators and some brokers.
- Operations Console: used by internal adjudicators and Support.

The system already had audit events for uploads and status changes, but it did not consistently capture recommendation display, checklist rule source, or carrier mapping failures. This gap contributed to confusion during the January 2026 incident.

## Proposed Components

### Claim Workspace API

The Claim Workspace API composes data from Claim Service, Document Service, Eligibility Service, and Integration Service. It does not own source-of-truth claim state. The API provides a role-filtered view of the workspace. It must call the Authorization Gateway before returning any PHI-bearing fields.

Key endpoints:

- GET /workspace/claims/{claimId}
- GET /workspace/claims/{claimId}/timeline
- POST /workspace/claims/{claimId}/override-recommendation
- POST /workspace/claims/{claimId}/missing-info-request
- GET /workspace/claims/{claimId}/carrier-sync

### Checklist and Recommendation Service

This service evaluates checklist rules and workflow recommendations. It receives claim references, not full document contents. It reads only metadata required for checklist evaluation: benefit type, state, employer group, carrier code, plan identifier, document type, evidence status, and eligibility flags. It must not persist raw OCR text.

Rules are versioned. Each checklist item must record a rule_source field. Sources may include default_carrier_rule, employer_plan_override, state_requirement, compliance_hold, or manual_exception. The service emits checklist_generated and recommendation_displayed events.

### Event Publisher Library

To reduce missing audit events, Meridian introduces a shared publisher library used by Workspace API, Recommendation Service, and Integration Service. The library enforces event schema validation, tenant ID presence, actor identity, and idempotency key generation. Services publish to the Polaris event bus, and Audit Service subscribes to claim workflow topics.

### Integration Status Adapter

The adapter normalizes carrier sync information from Integration Service. Carrier systems use inconsistent response codes. The adapter maps these to pending, succeeded, failed_retryable, failed_non_retryable, suppressed, and unknown. The UI displays user-friendly labels but preserves raw codes in internal logs.

## Data Flow

1. A claim enters Claim Service through portal intake, API intake, or manual creation.
2. Claim Service emits claim_received.
3. Document Service receives evidence uploads and emits evidence_uploaded after malware scan passes. Failed scan events are restricted to Security and SRE.
4. Checklist and Recommendation Service evaluates rules after claim metadata or evidence metadata changes.
5. Recommendation Service stores the recommendation record with fact references and emits recommendation_displayed.
6. Claim Workspace API displays role-filtered claim state, evidence status, checklist, recommendation, and integration state.
7. Adjudicator override or missing information request triggers Workspace API write endpoints.
8. Integration Service sends outbound payloads to carriers after final internal review.
9. Integration Status Adapter updates carrier sync state and publishes carrier_sync_failed or claim_sent_to_carrier events.
10. Audit Service stores append-only records and supports export.

## Event Model

All Meridian events must include:

- tenant_id
- claim_id
- event_name
- actor_type
- actor_id or system_actor
- timestamp_utc
- request_id
- idempotency_key
- schema_version
- source_service
- prior_value when applicable
- new_value when applicable
- evidence_reference_id when applicable

The event schema intentionally avoids embedding full evidence content. Evidence references are stable identifiers that can be resolved only by authorized services.

Event ordering is best-effort across services. Audit Service stores ingestion time and event timestamp. For user-facing timelines, the Workspace API sorts by event timestamp and then ingestion time. If timestamps differ by more than five minutes, the timeline displays a “sequence uncertain” marker to internal users. This marker is hidden from customers.

## Storage

Meridian stores additional workflow data in three tables:

### meridian_recommendations

Fields include recommendation_id, tenant_id, claim_id, recommendation_type, reason_code, displayed_text_key, input_fact_hash, input_fact_references, created_at, expires_at, schema_version, and suppressed_flag.

### meridian_checklist_items

Fields include checklist_item_id, tenant_id, claim_id, requirement_key, display_label_key, status, rule_source, source_rule_version, first_generated_at, last_updated_at, and resolved_at.

### carrier_sync_status_cache

Fields include tenant_id, claim_id, carrier_code, integration_job_id, normalized_status, raw_status_code, last_attempt_at, retry_count, next_retry_at, owner_team, and manually_suppressed_by.

These tables are not the system of record for final claim decisions. Claim Service remains the source of truth for public status and internal status.

## Retention Design

The Compliance Handbook defines retention as seven years after claim closure unless contract or legal hold requires longer. The design implements deletion eligibility at seven years plus 30 days after closure to account for delayed carrier callbacks, retry queues, backup snapshots, and operational reconciliation. This additional 30-day period is intended as a deletion processing buffer, not a new business retention rule.

Temporary recommendation evaluation traces that are not referenced by an audit event are deleted after 30 days. Recommendation records that were displayed to a user are retained with the claim audit history. OCR text remains in Document Service. Search indexes that include evidence-derived snippets must remain tenant-scoped and are purged according to Document Service retention schedules.

## Security Controls

Authorization Gateway is mandatory for all workspace reads. The API must pass requested field categories: claim_summary, eligibility_summary, evidence_metadata, evidence_content, carrier_sync_metadata, audit_history, and recommendation_details.

The broker role cannot view evidence_content by default. A broker can view limited evidence_metadata such as “provider statement received” only when the customer has enabled broker operational visibility. The broker-phi-view feature flag requires Security approval and a signed addendum.

Service-to-service calls use mTLS. Event bus topics are tenant-partitioned. Audit Service validates tenant ID and rejects cross-tenant event writes. All admin impersonation events must include original_actor_id and impersonation_reason.

## Failure Modes

If Recommendation Service is unavailable, the workspace should display claim data without recommendations and emit recommendation_unavailable_metric, but it must not block adjudicator review. If Checklist Service is unavailable, missing information templates may be disabled, because templates depend on checklist rule source.

If Audit Service is unavailable, write operations that change claim state must fail closed. Read-only workspace views may remain available. This differs from the older Operations Console, which allowed some status changes when audit ingestion lagged. The new behavior was required by Security Review SR-2026-02-MER.

If Integration Service is unavailable, carrier sync state should show “pending carrier transmission” and SRE should be paged only if retry backlog exceeds threshold for 30 minutes.

## Observability

Required metrics include workspace_api_latency, workspace_authz_denied, recommendation_eval_latency, recommendation_display_count, recommendation_override_count, checklist_generation_failure, audit_publish_failure, carrier_sync_status_lag, and carrier_retry_backlog.

Required logs must include request_id, tenant_id, claim_id hash, source_service, actor_type, actor_id hash, and error category. Logs must not include full member name, SSN, diagnosis detail, uploaded evidence body, or claim notes containing PHI.

Distributed traces should follow request flow from Workspace API to downstream services. SRE noted that tracing headers are sometimes dropped by the legacy LumenBridge importer; fixing that importer is a Phase 2 task.

## Rollout Plan

Architecture supports feature flags at tenant, employer group, and role level. Pilot tenants are Ashvale Manufacturing, BluePeak Retail Group, and Corvus BioSystems. The Architecture Review Board required read-only workspace launch before write actions. The rollout sequence is:

1. Internal synthetic tenant testing.
2. Internal Operations read-only pilot.
3. Customer pilot with read-only recommendations.
4. Enable missing information request action.
5. Enable adjudicator override.
6. Enable carrier sync status display.
7. Retire legacy queue page for pilot tenants.

## Migration Considerations

Legacy LumenBridge claims use packet_id rather than claim_id. Migration maps packet_id to claim_id through the legacy_claim_alias table. If a packet lacks a current employer group mapping, it remains on the legacy queue. The migration job must not infer mappings based on employee name or email.

Existing documents with unknown evidence type are surfaced as “unclassified evidence.” Checklist Service may recommend manual classification, but it must not mark a required evidence item complete based on unknown type.

## Open Technical Decisions

- Whether to store recommendation input facts as structured JSON or hashed references with resolver metadata.
- Whether carrier_sync_status_cache should be populated synchronously after final review or asynchronously through event subscription.
- Whether to include audit export generation in Workspace API or keep it in Compliance Console.
- Whether the UI should display sequence uncertainty when event ordering is ambiguous.

## Accepted Conditions

The Architecture Review Board accepted the design on 2026-02-28 with the following conditions:

1. Security must review broker role filtering before customer pilot.
2. SRE must define pager thresholds for carrier retry backlog.
3. Product must confirm wording for recommendation banners.
4. Compliance must approve the audit export field list.
5. Platform must demonstrate tenant isolation tests before enabling customer data.

## Appendix: Example Event

```
event_name: recommendation_displayed
tenant_id: tnt_ashvale
claim_id: clm_782812
actor_type: system
system_actor: meridian_recommendation_service
timestamp_utc: 2026-02-21T14:22:05Z
reason_code: missing_provider_statement
input_fact_references:
  - claim.benefit_type
  - evidence.provider_statement.status
  - eligibility.coverage_active
schema_version: 1.0
```
