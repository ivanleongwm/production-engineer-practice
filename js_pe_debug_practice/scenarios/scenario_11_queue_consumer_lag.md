# Scenario 11 - Queue Consumer Lag

## Incident report

Client `C1111` received ACK for order `O1111` (NVDA, 150 shares) quickly, but the fill/position update arrived ~18 seconds late. Execution desk suspects the matching engine is slow.

## Goal

Determine whether the delay is in fill generation, publishing, or downstream consumption.

## Suggested commands to try (no answer)

- `grep -Rni "O1111\|E71111" logs/`
- `grep -Rni "consumer_lag\|lag_messages\|lag_ms" logs/`
- `grep -Rni "execution_published\|position_update" logs/`
- `less logs/position.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
