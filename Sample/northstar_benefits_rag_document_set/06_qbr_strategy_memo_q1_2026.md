# Q1 2026 Business Review and Strategy Memo

**Filename:** 06_qbr_strategy_memo_q1_2026.md  
**Document type:** Quarterly Business Review / Strategy Memo  
**Date:** 2026-04-08  
**Owner:** Noah Feld, VP Strategy and Operations  
**Status:** Shared with executive staff  
**Related documents:** 01_project_meridian_prd.md, 10_project_meridian_roadmap.md

## Purpose Summary

This memo summarizes Q1 business performance for Polaris Claims Hub and connects customer retention, operational efficiency, and Project Meridian rollout priorities.

## Executive Summary

Q1 revenue performance was slightly above plan, but service costs grew faster than expected because claim volume shifted toward more complex benefit types. Meridian remains the primary operational efficiency bet for 2026. The January classifier incident delayed the original launch schedule, but the phased rollout has improved confidence among Compliance and large brokers.

The executive team should continue funding Meridian, but should not frame it as pure automation. Customers are buying reliability, auditability, and fewer status escalations. The highest-value outcome is not replacing adjudicators; it is reducing avoidable rework.

## Q1 Metrics

- Annual recurring revenue: $42.8M, 4.2 percent above plan.
- Net revenue retention: 112 percent.
- Gross logo retention: 94 percent.
- Claims processed through Polaris: 318,000.
- Average claims per covered life: 0.42.
- Support escalations tagged “status unclear”: 1,842, up 18 percent from Q4.
- Median time to first human review: 18.1 business hours, slightly improved from 18.6.
- Carrier sync failures per 1,000 claims: 12.4.
- Duplicate evidence request rate: 9.7 percent.

## Customer Signals

Broker advisory board members consistently asked for clearer status visibility. They are less interested in algorithmic claim decisions than in knowing whether a claim is blocked by the employee, employer, Northstar, or carrier. Large employers asked for audit exports, especially when reconciling employee complaints.

Ashvale Manufacturing said Meridian’s unified workspace would reduce weekly broker calls if it can show safe evidence status and carrier transmission state. BluePeak Retail Group emphasized template clarity and asked that “medical statement” and “provider statement” not appear as separate requirements. Corvus BioSystems asked for stricter broker access and does not want broker PHI enabled.

## Strategic Priorities

1. Launch Meridian safely with pilot tenants.
2. Reduce duplicate evidence requests by at least 30 percent.
3. Improve carrier sync observability.
4. Strengthen compliance posture through audit exports.
5. Retire legacy LumenBridge terminology from customer-facing materials.
6. Expand broker operational visibility without exposing restricted evidence.

## Launch Delay Rationale

The shift from a single April launch to a phased rollout was the right decision. The January incident demonstrated that classifier errors can appear as customer action items, causing duplicate requests and trust erosion. It also showed that Support needs a better explanation layer. Product, SRE, and Compliance agreed that read-only visibility should precede workflow-changing actions.

Evidence supporting the delay appears in the incident postmortem, Product Council decision notes, and the roadmap. The delay was not caused by lack of customer demand; it was caused by reliability and auditability concerns.

## Financial View

The business case for Meridian depends on reducing manual rework. Operations estimates that duplicate evidence requests and unclear status escalations cost approximately 4,600 staff hours per quarter. A 30 percent reduction would save roughly 1,380 hours per quarter before considering customer satisfaction effects.

Engineering cost increased because Security required stronger event capture and role filtering. This cost is justified. A major data access incident would be far more expensive than a delayed launch.

## Risks

- Pilot customers may expect faster claim decisions even though Meridian is not an automated adjudication system.
- Broker visibility requests may pressure teams to overexpose evidence details.
- Carrier sync issues could be mistaken for Northstar review delays.
- Legacy LumenBridge customers may resist terminology changes.
- If audit export is delayed, Compliance value proposition weakens.

## Decisions

The executive staff endorsed continued investment in Meridian. The team approved hiring one additional Integration Engineer for carrier sync reliability and one Support Operations analyst for Meridian pilot readiness. The team rejected a proposal to market Meridian as AI adjudication.

## Next Quarter Focus

Q2 should focus on pilot conversion, operational training, and measurable reduction in duplicate requests. Product should report weekly on time to first review, recommendation override rate, and Support escalations. Strategy will revisit pricing only after customer pilots demonstrate value.

## Appendix: Customer Notes

Ashvale wants a weekly export of claims blocked by employer action. BluePeak wants terminology normalization. Corvus wants strict broker access. These requests are compatible with Meridian but should not all be treated as Phase 1 launch blockers.
