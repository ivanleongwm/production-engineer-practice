# Scenario 15 Solution - Exchange Session Disconnect

## Short answer / root cause

Order `O1515` was **accepted internally** (gateway ACK, risk accept, sent_to_exchange), but the **FIX session FIX-PROD-01 disconnected due to sequence mismatch** before exchange ack. Internal path OK; **exchange session broken**.

## Commands to run

```bash
grep -Rni "O1515" logs/
grep -Rni "FIX\|session_down\|sequence_mismatch" logs/
grep -Rni "sent_to_exchange\|exchange_ack_missing\|no_exchange_ack" logs/
less logs/system.log
```

## Important log lines to notice

- `gateway.log`: `ack_to_client status=ACK` — internal accept
- `gateway.log`: `sent_to_exchange session=FIX-PROD-01`
- `system.log`: `session_down session=FIX-PROD-01 reason=sequence_mismatch expected_seq=104882 received_seq=104880`
- `engine.log`: `exchange_ack_missing order_id=O1515 waited_ms=500`
- `client.log`: `no_exchange_ack internal_status=ACK exchange_status=UNKNOWN`

## Red herrings to ignore

- Fast internal ACK — does not mean exchange received the order
- Risk/engine heartbeats healthy — upstream of exchange break
- Unrelated kafka lag warnings

## First divergence

At **FIX session disconnect (sequence mismatch)** immediately after send — no exchange acknowledgement.

## Immediate mitigation

- Resync FIX session sequence with exchange (coordinate with exchange ops)
- Stop sending new orders on FIX-PROD-01 until session restored
- Reconcile open orders: internal NEW vs exchange unknown state

## Long-term fix

- Automated sequence gap detection and controlled resync procedure
- Separate internal ACK from exchange ACK in client UI/API
- Session health dashboard with sequence numbers and last ack time

## 60-second interview explanation

"O1515 got internal ACK but client sees no exchange ack. I traced through risk accept and sent_to_exchange on FIX-PROD-01, then system.log shows session_down for sequence_mismatch — expected 104882, got 104880. Engine logs exchange_ack_missing. First divergence is FIX session break, not gateway or risk. I'd halt the session, resync sequences with the exchange, reconcile order state, and never treat internal ACK as exchange confirmation."
