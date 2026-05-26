# Incident Postmortem: Intake Classification and Evidence Routing

**Filename:** 05_incident_postmortem_intake_classifier.md  
**Document type:** Incident Postmortem  
**Incident date:** 2026-01-22  
**Postmortem date:** 2026-01-29  
**Incident commander:** Lena Ortiz  
**Status:** Closed with follow-up actions open  
**Related documents:** 01_project_meridian_prd.md, 02_meridian_architecture_design.md, 03_operations_runbook_meridian.md

## Purpose Summary

This postmortem describes the January 22, 2026 intake classification incident that delayed several claim reviews and led to changes in the Meridian rollout plan, event logging requirements, and recommendation language controls.

## Summary

On January 22, 2026, a configuration change to the intake classifier caused supplemental accident evidence uploaded by two pilot-prep customers to be categorized as “unclassified evidence” instead of “incident report” or “provider statement.” The affected claims did not lose evidence files, and no unauthorized access was identified. However, 184 claims were routed to manual exception queues, 67 claims received duplicate missing information requests, and Support could not explain the delay from the standard status screen.

The issue was detected by an Operations lead who noticed an unusual spike in unclassified evidence for Ashvale Manufacturing. Automated monitoring did not alert because the legacy classifier dashboard grouped unclassified evidence under manual review and did not distinguish normal manual review from classifier regression.

## Impact

Affected tenants:
- Ashvale Manufacturing
- BluePeak Retail Group

Affected records:
- 184 claims routed to manual exception.
- 67 claims had duplicate missing information requests.
- 21 claims missed the internal first-review SLA.
- 0 confirmed unauthorized access events.
- 0 evidence files lost.

Customer impact was moderate. Claims were delayed, and some employees received confusing requests for documents they had already uploaded. Support escalations increased sharply on January 23 and January 24.

## Timeline

2026-01-22 09:12 ET: Classifier configuration version 2026.01.22-r1 deployed.

2026-01-22 10:04 ET: Evidence uploads for Ashvale begin receiving unclassified_evidence type.

2026-01-22 12:47 ET: Operations lead notices manual exception queue above normal range.

2026-01-22 13:10 ET: Support receives first broker escalation about duplicate document request.

2026-01-22 13:22 ET: SRE opens incident channel.

2026-01-22 13:41 ET: Platform rolls back classifier config to 2026.01.15-r3.

2026-01-22 14:20 ET: New uploads classify normally.

2026-01-22 16:05 ET: Backfill job identifies affected claims.

2026-01-23 09:30 ET: Customer communication sent to Ashvale and BluePeak.

2026-01-24 15:00 ET: Duplicate request suppression script completed.

2026-01-29 11:00 ET: Postmortem reviewed by Product, Compliance, SRE, and Operations.

## Root Cause

The immediate cause was a classifier rule change that renamed “provider statement” to “medical statement” for one carrier template but unintentionally narrowed the synonym list used by the supplemental accident classifier. The regression test suite covered standard document examples but did not include Ashvale’s employer-custom incident report format or BluePeak’s scanned provider statement template.

A contributing factor was the absence of a clear event trail from evidence upload to checklist generation. Support could see that a claim was pending information but could not see that the uploaded document had been classified as unclassified evidence. Another contributing factor was that duplicate missing information requests were permitted when a checklist item was regenerated after classifier rollback.

## What Went Well

- Evidence files remained intact.
- Rollback was completed in under 30 minutes after incident declaration.
- Operations identified the issue quickly despite insufficient automated detection.
- The backfill job found affected claims without requiring customer re-upload.
- Compliance confirmed that no unauthorized access was detected.

## What Did Not Go Well

- Monitoring did not alert on classifier regression.
- Support status views did not distinguish missing customer evidence from internal classification delay.
- Duplicate missing information requests were sent.
- The launch plan assumed that classifier behavior could be validated separately from checklist behavior.
- Event logs did not consistently show recommendation or checklist source.

## Corrective Actions

| Action | Owner | Due Date | Status |
|---|---|---:|---|
| Add classifier regression suite using pilot customer document samples | Platform Engineering | 2026-02-10 | Done |
| Add unclassified evidence spike alert by tenant and benefit type | SRE | 2026-02-05 | Done |
| Require checklist rule source in workspace | Product / Platform | 2026-02-20 | Done in Meridian design |
| Suppress duplicate missing information requests within 72 hours | Platform Engineering | 2026-02-18 | Done |
| Revise rollout from big-bang launch to phased pilot | Product Council | 2026-02-01 | Done |
| Add recommendation_displayed audit event | Platform Engineering | 2026-02-28 | In progress at review |
| Update Support KB for classification delay language | Support Ops | 2026-02-08 | Done |

## Rollout Implications

The original Meridian rollout plan targeted a single customer-facing launch in April 2026. After this incident, Product Council approved a phased rollout. Phase 1 begins with read-only recommendations and role-filtered workspace visibility. Write actions such as missing information templates and adjudicator override are enabled after audit and checklist reliability checks.

The incident also changed the wording policy for recommendations. Product and Compliance agreed that recommendations must not imply final decisions. The language “ready to approve” was removed and replaced with “eligible for human review.”

## Customer Communications

Support sent a plain-language explanation to Ashvale and BluePeak. The message stated that uploaded evidence had been received but some documents were temporarily categorized incorrectly, which delayed review and caused duplicate requests. The message did not reference internal classifier rules or model terminology.

## Lessons for RAG Testing

This incident is useful for testing retrieval because the evidence for delayed launch is spread across this postmortem, the PRD, the decision log, and the roadmap. A grounded answer should cite the classification regression, duplicate missing information requests, missing event traceability, and the Product Council decision to phase rollout.

## Appendix: Detection Gap

The legacy classifier dashboard reported total manual review volume but not document type regression. SRE’s new alert computes the ratio of unclassified evidence to total evidence uploads by tenant and benefit type. Alert threshold is 8 percent for 15 minutes in pilot tenants. Baseline for Ashvale supplemental accident is below 2 percent.
