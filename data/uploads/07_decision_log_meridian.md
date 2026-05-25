# Meridian Meeting Notes and Decision Log

**Filename:** 07_decision_log_meridian.md  
**Document type:** Meeting Notes / Decision Log  
**Date range:** 2025-11-07 to 2026-03-18  
**Owner:** Priya Menon  
**Status:** Living record  
**Related documents:** 01_project_meridian_prd.md, 05_incident_postmortem_intake_classifier.md, 10_project_meridian_roadmap.md

## Purpose Summary

This file captures major Meridian decisions, unresolved questions, and action items. It intentionally preserves some historical terminology used before the final PRD.

## D-001: Standardize Product Term “Claim”

**Date:** 2025-11-07  
**Decision:** Use “claim” in Meridian UI. Preserve legacy aliases for import and search.  
**Context:** LumenBridge used “packet,” some brokers say “case,” and older Support macros say “matter.”  
**Owner:** Product  
**Status:** Accepted

## D-004: Exclude Automated Denial

**Date:** 2025-12-02  
**Decision:** Meridian recommendations will not deny claims or make final benefit determinations.  
**Rationale:** Compliance and customer trust concerns.  
**Status:** Accepted

## D-007: Keep Claim Service as Source of Truth

**Date:** 2025-12-16  
**Decision:** Phase 1 will not replace Claim Service. Workspace API composes data from existing systems.  
**Owner:** Platform Engineering  
**Status:** Accepted

## D-010: Audit Export Required for Pilot

**Date:** 2026-01-05  
**Decision:** Compliance users need CSV audit export in Phase 1. Signed JSON can wait.  
**Open issue:** Whether export belongs in Workspace API or Compliance Console.  
**Status:** Accepted with implementation owner unresolved

## D-014: Terminology Decision

**Date:** 2026-01-11  
**Decision:** Preferred term is “claim evidence package,” not “packet.”  
**Notes:** Support macros still use “case” in several templates.  
**Status:** Accepted

## D-018: Rollout Plan Revised After Classifier Incident

**Date:** 2026-01-31  
**Decision:** Replace big-bang April launch with phased rollout. Read-only workspace and recommendations first; write actions later.  
**Evidence:** January 22 classifier incident caused unclassified evidence spike, duplicate missing information requests, and support confusion.  
**Owner:** Product Council  
**Status:** Accepted

## D-019: Recommendation Language Restrictions

**Date:** 2026-01-31  
**Decision:** Recommendations may not use “deny,” “approve,” or equivalent final-decision language.  
**Approved examples:** missing provider statement, possible duplicate claim, carrier mapping error, ready for human review.  
**Status:** Accepted

## D-021: Broker PHI Access Flag

**Date:** 2026-02-06  
**Decision:** Broker PHI access must be controlled by feature flag and signed addendum. Default is off.  
**Owner:** Security  
**Status:** Accepted

## D-024: Retention Interpretation

**Date:** 2026-02-13  
**Decision:** Compliance policy remains seven years after claim closure. Engineering may implement deletion eligibility with a 30-day processing buffer.  
**Notes:** Do not describe this as seven years and 30 days in customer-facing policy.  
**Status:** Accepted

## D-026: Carrier Sync Visibility

**Date:** 2026-02-17  
**Decision:** Workspace must show normalized carrier sync status for internal users. Customer visibility deferred.  
**Reason:** Brokers cannot tell whether delays are internal or carrier-side.  
**Status:** Accepted for internal pilot

## D-030: Missing Information Template Lock

**Date:** 2026-02-24  
**Decision:** Required compliance language in missing information templates cannot be removed by employer admins.  
**Owner:** Compliance  
**Status:** Accepted

## D-033: Pilot Tenant List

**Date:** 2026-03-05  
**Decision:** Pilot tenants are Ashvale Manufacturing, BluePeak Retail Group, and Corvus BioSystems.  
**Constraints:** Corvus broker PHI remains disabled. BluePeak requires terminology mapping patch. Ashvale has custom employer confirmation rule.  
**Status:** Accepted

## D-036: Reopened Claim SLA

**Date:** 2026-03-18  
**Decision:** No final decision. Operations wants new internal SLA timer after reopen; Compliance says retention should be based on final closure.  
**Status:** Open

## Action Items

- Product to remove “case” from Support macros by end of Q2.
- Platform to finish event publisher migration.
- SRE to publish carrier retry backlog threshold.
- Compliance to approve final audit export fields.
- Support Ops to train pilot teams on status explanation language.
