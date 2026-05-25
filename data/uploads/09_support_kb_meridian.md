# Support Knowledge Base: Meridian Claim Workspace

**Filename:** 09_support_kb_meridian.md  
**Document type:** FAQ / Support Knowledge Base Article  
**Date:** 2026-03-22  
**Owner:** Support Operations  
**Status:** Active for Support and Support Leads  
**Related documents:** 03_operations_runbook_meridian.md, 08_customer_onboarding_guide.md

## Purpose Summary

This article gives Support teams approved explanations and troubleshooting steps for Meridian pilot questions.

## Quick Positioning

Meridian is a workflow and visibility improvement in Polaris Claims Hub. It helps Northstar teams understand claim status, evidence needs, recommendations, and carrier transmission state. It does not automatically approve or deny claims.

## Who Can Use Meridian?

During pilot, Meridian is enabled for Ashvale Manufacturing, BluePeak Retail Group, and Corvus BioSystems. Some customer users see only limited status improvements. Internal Operations users see the full workspace based on role permissions.

## What Should I Say If a Broker Asks Why a Claim Is Delayed?

Use the safest accurate reason available. Examples:
- “We have received the claim and it is under review.”
- “We are waiting for additional information requested through the portal.”
- “The claim has been prepared for carrier transmission.”
- “We are reviewing uploaded evidence before the next status update.”

Do not mention internal audit hold, classifier regression, model confidence, or restricted evidence details. If the broker has no PHI access, do not describe medical documents beyond safe labels such as “provider statement received” if enabled.

## Duplicate Evidence Requests

If a customer says they received a duplicate request, check the claim timeline for recent missing information requests and evidence uploads. Duplicate requests were a known issue after the January classifier incident, but the suppression rule should prevent repeat requests within 72 hours. If a duplicate occurred after 2026-02-18, escalate to Platform Engineering.

Suggested response: “We see that evidence was uploaded. We are checking whether the request was sent before the upload was matched to the claim.”

## Recommendation Banner Questions

Recommendations are internal workflow aids. Do not read recommendation text to customers unless the text is already customer-approved status language. Never say the system decided a claim outcome.

## Carrier Sync Questions

If carrier status is pending or failed, check whether the customer-facing status should remain under review or sent to carrier. Do not promise carrier receipt unless status is succeeded or Integration confirms it. Common internal reasons include missing carrier group ID, unsupported benefit code, carrier portal unavailable, or payload validation failed.

## Access Issues

If a user cannot see expected information:
1. Confirm tenant and employer group.
2. Confirm user role.
3. Confirm whether broker PHI access is enabled.
4. Check whether the claim belongs to a Meridian-enabled pilot group.
5. Escalate suspected access defects to Security.

Never request that a user share another employee’s medical documents in a normal email thread.

## Reopened Claims

A reopened claim may appear with prior history and new activity. The reopened claim SLA timer is still under discussion. Do not state a policy that is not documented. You may say: “The claim has been reopened and is being reviewed under the current workflow.”

## Approved Terms

Use claim, evidence, provider statement, incident report, employer confirmation, pending information, under review, sent to carrier, decision received, closed, reopened.

Avoid packet, case, matter, AI decision, automatic denial, fraud likely, medically insufficient.

## When to Escalate

Escalate to SRE for broad workspace outage, repeated timeouts, or multiple customers impacted. Escalate to Platform for checklist mismatch or duplicate request after suppression date. Escalate to Integration for carrier sync failures. Escalate to Security for possible unauthorized access or PHI exposure. Escalate to Compliance for retention, legal hold, or privacy requests.

## FAQ

**Does Meridian decide claims?**  
No. Meridian provides workflow visibility and non-binding internal recommendations. Human adjudicators remain responsible for claim review actions.

**Why does the customer guide say carrier status is internal?**  
Carrier sync visibility is being tested internally first because raw carrier errors can be confusing and may include configuration details.

**Can Support export audit history for a customer?**  
No. Compliance users handle audit exports. Support can collect the request and route it to Compliance.

**What if the uploaded document label looks wrong?**  
Check whether the customer uses alternate terminology. BluePeak’s “medical statement” maps to “provider statement.” If the document remains unclassified, escalate.

**What retention period should I quote?**  
Use seven years after claim closure unless contract or legal hold requires longer. Do not mention engineering deletion buffers to customers.
