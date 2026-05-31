# Scenario 15 - Exchange Session Disconnect

## Incident report

Order `O1515` (AAPL, 100 shares) received internal ACK from gateway, but client reports no exchange acknowledgement. Internal systems look fine through risk.

## Goal

Distinguish internal acceptance from exchange-side acknowledgement.

## Suggested commands to try (no answer)

- `grep -Rni "O1515" logs/`
- `grep -Rni "FIX\|session_down\|sequence_mismatch\|exchange_ack" logs/`
- `grep -Rni "sent_to_exchange\|no_exchange_ack" logs/`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
