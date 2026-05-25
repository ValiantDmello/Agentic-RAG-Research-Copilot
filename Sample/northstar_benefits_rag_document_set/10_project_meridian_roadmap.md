# Project Meridian Roadmap and Delivery Plan

**Filename:** 10_project_meridian_roadmap.md  
**Document type:** Project Plan / Roadmap  
**Date:** 2026-03-25  
**Owner:** Anika Rao, Program Management  
**Status:** Baseline plan after rollout revision  
**Related documents:** 01_project_meridian_prd.md, 06_qbr_strategy_memo_q1_2026.md, 07_decision_log_meridian.md

## Purpose Summary

This roadmap tracks Meridian delivery milestones, owners, dependencies, risks, and scope changes after the January 2026 classifier incident.

## Program Objective

Deliver a reliable, compliant, and auditable claim workspace that reduces duplicate evidence requests, improves time to first human review, and gives Support better status explanations without exposing restricted data.

## Major Milestones

### Milestone 1: Foundation Complete

**Target:** 2026-03-15  
**Status:** Complete  
**Scope:** Workspace API read model, feature flags, role-filtered views, event publisher library beta, recommendation schema, checklist rule versioning.

### Milestone 2: Internal Operations Pilot

**Target:** 2026-04-08  
**Status:** On track  
**Scope:** Read-only workspace for pilot tenants, recommendation display, checklist visibility, audit timeline, Support training.

### Milestone 3: Controlled Write Actions

**Target:** 2026-04-22  
**Status:** At risk  
**Scope:** Missing information templates, adjudicator override, duplicate request suppression validation, audit fail-closed behavior.

### Milestone 4: Carrier Sync Visibility

**Target:** 2026-05-06  
**Status:** On track with Integration hiring risk  
**Scope:** Normalized carrier sync status, retry backlog dashboard, mapping error workflow, manual suppression reason capture.

### Milestone 5: Customer Pilot Expansion

**Target:** 2026-05-20  
**Status:** Dependent on Milestone 3 and 4  
**Scope:** Expand pilot to additional employer groups within Ashvale and BluePeak. Corvus expansion depends on broker access review.

### Milestone 6: Legacy Queue Retirement for Pilot Tenants

**Target:** 2026-06-17  
**Status:** Not started  
**Scope:** Disable legacy queue page for pilot tenants after success metrics meet thresholds for four consecutive weeks.

## Scope Changes Since Original Plan

The original plan assumed a single April launch including read-only workspace, write actions, bulk evidence upload, carrier sync visibility, and customer-facing status improvements. The revised plan separates these into milestones.

Removed from Phase 1:
- Bulk evidence upload.
- Customer-facing carrier error details.
- Signed JSON audit export.
- Automated evidence deduplication beyond duplicate request suppression.
- Localization for Quebec customers.

Added to Phase 1:
- recommendation_displayed audit event.
- Checklist rule source display.
- Audit fail-closed requirement for state-changing actions.
- Broker PHI access feature flag review.
- Unclassified evidence spike monitoring.

## Dependency Matrix

| Dependency | Owner | Needed For | Risk |
|---|---|---|---|
| Security role-filter review | Security | Internal and customer pilot | Medium |
| Audit export field approval | Compliance | Pilot readiness | Medium |
| Event publisher migration | Platform | Write actions | High |
| Carrier retry dashboard | Integration / SRE | Carrier visibility | Medium |
| Support training | Support Ops | Pilot launch | Low |
| BluePeak terminology patch | Platform | BluePeak pilot | Low |
| Ashvale employer confirmation rule | Product / Platform | Ashvale carrier sync | Medium |
| Corvus broker access review | Security / CS | Corvus expansion | Medium |

## Success Metrics

- Median time to first human review below 10 business hours for pilot tenants.
- Duplicate evidence request rate reduced by 30 percent from Q4 baseline.
- 99 percent of claim-changing actions have complete audit event confirmation.
- Recommendation override rate reviewed weekly and not exceeding expected thresholds without explanation.
- Carrier sync success within two hours for 95 percent of internally completed pilot claims.
- Support escalations tagged “status unclear” reduced by 20 percent for pilot tenants.

## Workstreams

### Product

Owns PRD updates, UI language, customer feedback, recommendation wording, and scope tradeoffs. Product also owns the terminology cleanup effort to remove “case” from Support macros and “packet” from customer-facing materials.

### Platform Engineering

Owns Workspace API, Checklist and Recommendation Service, event publisher library, UI integration, and duplicate request suppression. The highest-risk item is event publisher migration because write actions cannot launch without audit fail-closed behavior.

### Integration Engineering

Owns carrier sync status adapter, retry dashboard, mapping error workflows, and manual suppression logging. QBR approved one additional Integration Engineer because carrier sync reliability is strategically important.

### SRE

Owns monitors, incident response, rollback, synthetic tenant checks, and dashboards. SRE also validates that read-only degradation works when Recommendation Service is unavailable.

### Compliance and Security

Own policy interpretation, role-based access review, broker PHI feature flag, audit export approval, and incident reporting obligations. Compliance clarified that retention policy is seven years after claim closure, while engineering may use a 30-day deletion processing buffer.

### Support Operations

Owns training, KB updates, customer-safe language, escalation routing, and feedback collection. Support must not expose internal recommendation or classifier details.

## Risks and Mitigations

**Risk:** Write actions launch before audit publisher is reliable.  
**Mitigation:** Milestone 3 cannot complete until audit fail-closed tests pass.

**Risk:** Customers interpret recommendations as automated adjudication.  
**Mitigation:** Recommendation language restrictions, training, and UI labels.

**Risk:** Carrier sync status causes confusion.  
**Mitigation:** Internal visibility first, customer-facing details deferred.

**Risk:** Pilot-specific plan terminology causes checklist mismatch.  
**Mitigation:** Rule source display and customer-specific terminology mapping.

**Risk:** Retention period described inconsistently.  
**Mitigation:** Customer-facing materials quote Compliance Handbook only.

## Governance

Weekly Meridian program review occurs Wednesdays at 11:00 ET. Product Council reviews scope changes. Architecture Review Board reviews material service design changes. Security Review is mandatory for access model changes. Compliance signs off on customer-facing policy language.

## Appendix: Evidence for Launch Delay

The delay was based on specific operational findings, not general caution. The January 22 classifier incident caused unclassified evidence routing, duplicate missing information requests, and status confusion. The incident led to Decision D-018, which replaced the big-bang launch with phased rollout. The roadmap reflects that decision by splitting read-only visibility, write actions, and carrier visibility into separate milestones.
