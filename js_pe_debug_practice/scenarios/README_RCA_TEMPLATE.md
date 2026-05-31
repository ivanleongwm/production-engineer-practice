# RCA Template

Copy this template into your notes for each scenario investigation.

## Incident summary

What happened? One or two sentences in plain language.

## User impact

Who is affected and how? (e.g., one client cannot submit, all fills delayed, position wrong)

## Scope

- Affected: order IDs, client IDs, symbols, hosts, environments
- Not affected: what still works normally

## Expected path

Describe the normal flow for this order type:

`client -> gateway -> risk -> engine -> execution publisher -> position`

## Actual path

Where did the order actually go? Where did it stop or diverge?

## First divergence

The earliest point where actual behavior differs from expected. Include log file and key fields.

## Evidence

Bullet list of log lines that support your conclusion. Include correlation keys (`order_id`, `trace_id`, `exec_id`).

## Root cause

One clear sentence. Name the failing layer (DNS, firewall, process, config, consumer, etc.).

## Immediate mitigation

What would you do in the next 15 minutes to reduce user impact?

## Long-term fix

What permanent change prevents recurrence?

## Interview explanation (60 seconds)

Practice saying this out loud:

> "The user reported [X]. I searched logs by [correlation key] and confirmed the expected path through [services]. The first divergence was at [layer/event] because [evidence]. This is not [red herring] because [reason]. Immediate mitigation is [Y]. Long-term fix is [Z]."
