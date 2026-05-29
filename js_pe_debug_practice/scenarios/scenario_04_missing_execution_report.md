# Scenario 04 - Missing Execution Report

## Incident report

Trader says: "Order O4004 got ACKed, but no fill/execution report ever came back."

## Goal

Identify where the order path breaks after matching engine fill generation.

## Suggested commands to try (no answer)

- `grep -Rni "O4004" logs/`
- `grep -Rni "E5404\\|publish\\|kafka\\|topic" logs/`
- `less logs/engine.log`
- `less logs/execution_publisher.log`
- `less logs/system.log`

## Your notes

- expected behavior:
- actual behavior:
- correlation key:
- system path:
- first divergence:
- hypothesis:
- verification:
- fix:
- prevention:
