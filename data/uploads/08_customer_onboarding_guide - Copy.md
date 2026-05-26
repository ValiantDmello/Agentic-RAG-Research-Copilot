# Customer Implementation Guide: Polaris Claims Hub with Meridian Pilot

**Filename:** 08_customer_onboarding_guide.md  
**Document type:** Customer Implementation / Onboarding Guide  
**Date:** 2026-03-20  
**Owner:** Customer Success Enablement  
**Status:** Pilot customer version  
**Related documents:** 04_compliance_security_handbook.md, 09_support_kb_meridian.md

## Purpose Summary

This guide explains how pilot customers prepare for Meridian-enabled workflows in Polaris Claims Hub. It is written for employer benefits administrators and broker operations leads.

## Overview

Meridian provides a clearer claim workspace for Northstar internal teams and selected customer-facing users. During the pilot, customers will see improved claim status descriptions and evidence request clarity. Meridian does not change plan benefits, carrier decision rules, or employee eligibility requirements.

## Pilot Timeline

- March 25, 2026: Customer configuration review.
- April 1, 2026: Administrator training.
- April 8, 2026: Read-only status visibility enabled.
- April 15, 2026: Missing information templates enabled for pilot Operations teams.
- April 29, 2026: Carrier sync status reviewed internally.
- May 2026: Pilot feedback and expansion decision.

Dates may shift if security review, audit validation, or tenant-specific configuration is incomplete.

## Customer Preparation Checklist

1. Confirm employer group list and plan identifiers.
2. Review benefit types included in the pilot.
3. Confirm broker access preferences.
4. Provide current evidence requirement language for each benefit type.
5. Identify customer contacts for claim escalation.
6. Attend administrator training.
7. Validate that legacy “packet” terminology is not used in customer-facing instructions.

## Evidence Upload Guidance

Customers should upload documents through the Polaris portal. Evidence types may include provider statement, incident report, employer confirmation, employee attestation, carrier form, wage statement, or other supporting document. If a document type is not listed, choose “other evidence” and add a note.

For BluePeak Retail Group, “medical statement” in older plan language is mapped to “provider statement” in Meridian. Customers should not upload the same document twice under both labels.

## Broker Access

Broker users receive operational status fields approved by the employer. By default, brokers cannot view uploaded medical evidence. Broker PHI access requires a signed addendum and Northstar Security approval. Corvus BioSystems has chosen not to enable broker PHI access during the pilot.

## Status Descriptions

Public statuses include received, pending information, under review, sent to carrier, decision received, closed, and reopened. Internal statuses such as audit hold or classification pending are not shown to customer users. If a claim is delayed because Northstar is validating uploaded evidence, Support may describe it as “under review” or “pending internal review,” depending on customer configuration.

## Missing Information Requests

Customers may receive missing information requests through portal notification and email. Requests will include the claim reference, requested item, due date where applicable, and required compliance language. Customers should not reply with sensitive documents over regular email unless instructed to use a secure channel.

## Carrier Transmission

During the early pilot, carrier sync status is primarily visible to Northstar internal teams. Customers may see “sent to carrier” after Northstar transmits the claim. A claim may be internally complete before carrier confirmation is available.

## Data Handling

Northstar retains claim records and evidence according to the Compliance Handbook. The standard policy is seven years after claim closure unless a contract or legal hold requires a longer period. Customers should not ask employees to send medical evidence to personal email accounts.

## Training Agenda

Training covers:
- Portal navigation.
- Evidence upload best practices.
- Status meanings.
- Broker access options.
- Escalation process.
- What Meridian does not do.
- Privacy and secure document handling.

## Common Implementation Risks

- Plan documents use terminology that differs from Meridian checklist labels.
- Broker role expectations are broader than approved access.
- Customer assumes Meridian automatically approves or denies claims.
- Employer administrators upload duplicate evidence after receiving a reminder.
- Carrier delays are mistaken for Northstar review delays.

## Escalation Contacts

Customer Success Manager owns onboarding coordination. Support owns day-to-day claim questions. Security handles access concerns. Compliance handles retention or privacy questions. Integration Engineering may be pulled in for carrier transmission issues but is not a direct customer contact.

## Appendix: Pilot-Specific Notes

Ashvale Manufacturing requires employer confirmation before supplemental accident claims are transmitted to carrier. BluePeak has terminology mapping for medical statement/provider statement. Corvus has broker PHI disabled and requires all broker status exports to exclude evidence details.
