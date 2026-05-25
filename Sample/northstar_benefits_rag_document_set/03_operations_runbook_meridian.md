# Meridian Operations Runbook

**Filename:** 03_operations_runbook_meridian.md  
**Document type:** Operations Runbook  
**Date:** 2026-03-12  
**Owner:** Lena Ortiz, Senior SRE Manager  
**Status:** Active for pilot tenants  
**Related documents:** 02_meridian_architecture_design.md, 05_incident_postmortem_intake_classifier.md, 09_support_kb_meridian.md

## Purpose Summary

This runbook describes how Support Operations, SRE, Platform Engineering, and Integration Engineering should monitor and respond to Meridian workspace issues during pilot and staged rollout.

## Scope

This runbook applies to Meridian-enabled tenants in Polaris Claims Hub. As of 2026-03-12, enabled pilot tenants are Ashvale Manufacturing, BluePeak Retail Group, and Corvus BioSystems. The runbook covers workspace loading failures, authorization denials, recommendation unavailability, audit publish failures, checklist errors, and carrier synchronization backlog.

## Team Responsibilities

**Support Operations** triages customer-visible issues, confirms tenant and role, checks the Support KB, gathers claim identifiers, and escalates to SRE or Platform Engineering when customer impact is confirmed. Support should not request screenshots that expose medical evidence unless a secure upload channel is used.

**SRE** owns incident coordination, service health, alert thresholds, paging, rollback, and post-incident timeline capture. SRE also owns the synthetic tenant monitor that creates a test claim, uploads mock evidence, and validates checklist generation every four hours.

**Platform Engineering** owns Workspace API, Recommendation Service, Checklist Service, event publisher library, and the UI shell used by Operations Console.

**Integration Engineering** owns carrier sync status, outbound payload retries, mapping errors, and Integration Status Adapter.

**Security** owns access-control validation and investigations involving suspected unauthorized access.

## Severity Definitions

Sev-1: Unauthorized access to restricted evidence, cross-tenant data exposure, or widespread inability to process claims for all Meridian tenants. Immediate incident response required.

Sev-2: Claim-changing actions unavailable for more than 30 minutes for pilot tenants, audit event publish failure for state-changing actions, or carrier sync backlog exceeding threshold for more than 60 minutes.

Sev-3: Recommendation banners unavailable while workspace remains usable, delayed checklist generation, single-tenant carrier mapping error, or Support-only reporting issues.

Sev-4: Cosmetic UI issue, stale non-critical dashboard, or documentation mismatch.

## Standard Triage Checklist

1. Confirm tenant name, employer group, claim ID, user role, and browser or API source.
2. Check whether tenant has Meridian feature flag enabled.
3. Determine whether the issue affects read-only workspace, write action, recommendation, checklist, audit timeline, or carrier sync.
4. Check current status of Workspace API, Recommendation Service, Checklist Service, Audit Service, and Integration Service.
5. Review logs using request_id where available. Do not search by employee name.
6. Confirm whether the user is authorized for the field category in question.
7. If customer-visible, create an incident channel and assign a commander for Sev-1 or Sev-2.

## Workspace Does Not Load

A workspace load failure usually appears as an HTTP 500, timeout, or blank panel. First check Workspace API latency and downstream dependency errors. If Authorization Gateway denies access, the UI should show a permissions message rather than a blank page.

Common causes:
- Claim ID belongs to a non-Meridian tenant.
- Legacy LumenBridge packet lacks claim alias mapping.
- Authorization Gateway has stale role cache.
- Eligibility Service timeout.
- Workspace API deploy with incompatible response schema.

Mitigation:
- For stale role cache, flush the tenant role cache using the internal admin job after Security approval.
- For non-Meridian tenants, instruct Support to use legacy Operations Console.
- For downstream timeout, SRE may temporarily lower evidence metadata expansion, but cannot bypass Authorization Gateway.

## Recommendation Unavailable

Recommendation Service is non-blocking. If unavailable, workspace should load without a recommendation banner. SRE should page Platform Engineering if recommendation_eval_error_rate exceeds 5 percent for 15 minutes on pilot tenants. Support should tell customers that claim review can continue and that recommendations are internal workflow aids.

Do not manually create recommendation records. Adjudicators may proceed with manual review and record reasons in claim notes. If recommendations are absent for more than one business day, Product must decide whether to pause rollout.

## Checklist Generation Failure

Checklist failure affects missing information templates. The UI should disable template send actions when rule_source cannot be determined. Platform Engineering should review checklist_generation_failure logs and compare rule version with the employer group plan configuration.

Known issue: For BluePeak Retail Group, plan BP-STDI-2025 uses the phrase “medical statement” in its plan document, while the default rule uses “provider statement.” The mapping was patched in rule version 2026.03.04-r2.

## Audit Publish Failure

State-changing writes must fail closed if Audit Service cannot confirm event acceptance. If users report that they cannot send missing information requests or override recommendations, check audit_publish_failure first.

Emergency action:
- Do not disable audit publishing.
- Do not backfill events manually from UI screenshots.
- Platform Engineering may replay failed events from the outbox table only when idempotency keys are intact.
- Compliance must be notified for any gap in claim-changing event capture.

## Carrier Sync Backlog

Carrier sync backlog is owned by Integration Engineering. Page Integration Engineering when retry backlog for Meridian claims exceeds 1,500 jobs or when oldest retry age exceeds 30 minutes for pilot tenants. The threshold is lower than the general Integration Service threshold because pilot brokers are monitoring Meridian status closely.

Common carrier sync error categories:
- missing_carrier_group_id
- unsupported_benefit_code
- carrier_portal_unavailable
- payload_validation_failed
- suppressed_by_manual_hold
- unknown_response

Manual suppression requires an Integration Engineering lead and must be recorded with reason. Suppression does not close the claim.

## Rollback

Meridian feature flags allow tenant-level and role-level rollback. Rollback options:

- Disable recommendation display only.
- Disable checklist templates.
- Disable write actions while preserving read-only workspace.
- Disable entire Meridian workspace and return tenant to legacy queues.

The preferred rollback for unclear incidents is to disable write actions first. Full rollback should be used for suspected authorization or cross-tenant issues. SRE owns execution, Product owns customer communication, and Security must approve any rollback related to access concerns.

## Communications

For Sev-1 and Sev-2 incidents, SRE opens an incident channel using the pattern `inc-meridian-yyyy-mm-dd-shortname`. Support posts customer impact summaries every 30 minutes while the incident is active. Avoid mentioning claim details in channel names.

Customer messaging should distinguish between claim processing delays and carrier transmission delays. Support must not promise that a carrier has received a claim unless the carrier sync status is succeeded or the Integration team confirms receipt.

## Post-Incident Requirements

Every Sev-1 and Sev-2 Meridian incident requires a postmortem within five business days. The postmortem must include timeline, impact, contributing factors, detection path, what worked, what did not work, action items, and customer communication summary. If an audit gap occurred, Compliance adds a separate regulatory assessment.

## Appendix A: Dashboards

Dashboards:
- Meridian Workspace Health
- Recommendation Service Quality
- Checklist Rule Errors
- Audit Event Outbox
- Carrier Retry Backlog
- Pilot Tenant Claim Throughput

## Appendix B: Known Pilot Exceptions

Ashvale Manufacturing has a custom plan rule that requires employer confirmation before carrier sync for supplemental accident claims. Corvus BioSystems has broker PHI access disabled even though the broker has operational visibility. BluePeak has a known plan terminology mapping issue described above.
