# Scenario 16 Solution - Clock Skew / Misleading Timestamps

## Short answer / root cause

**engine-host-2 clock is skewed +4.8 seconds** (NTP warning), making engine timestamps appear *before* gateway events. **Monotonic seq IDs** (1616001+) prove correct order: gateway → risk → engine.

## Commands to run

```bash
grep -Rni "O1616" logs/
grep -Rni "clock_offset\|ntp\|host_clock_skew" logs/system.log
grep -Rni "seq=" logs/ | grep O1616
grep -h "O1616" logs/* | sort
less logs/system.log
```

## Important log lines to notice

- `system.log`: `clock_offset offset_s=4.8 host=engine-host-2 action=step_scheduled`
- `engine.log`: `order_received ... host_clock_skew_s=4.8 note=timestamp_appears_before_gateway_due_to_skew`
- Compare `ts=` on engine vs gateway — engine ts earlier despite later seq
- `seq=1616001` gateway risk → `seq=1616002` ack → `seq=1616003` engine receive — logical order

## Red herrings to ignore

- Raw timestamp ordering across hosts without seq correlation
- timezone_mismatch display warnings at end of logs
- Assuming engine processed early — seq proves otherwise

## First divergence

**Apparent** divergence at engine timestamp vs gateway — **real** issue is clock skew on engine-host-2, not out-of-order processing.

## Immediate mitigation

- Force NTP step/chrony sync on engine-host-2
- Temporarily drain traffic from skewed host
- Use seq/trace_id for incident timelines, not cross-host ts alone

## Long-term fix

- Alert on |clock_offset| > threshold; block host from pool if skewed
- Log both wall-clock and monotonic/seq on every hop
- Centralized event timeline tool using correlation IDs

## 60-second interview explanation

"Logs look like engine received O1616 before gateway sent it. System.log shows engine-host-2 NTP offset 4.8s. Engine log explicitly flags host_clock_skew. Seq numbers increase gateway→risk→engine, proving correct order despite bad timestamps. First divergence is clock skew, not routing logic. I'd sync NTP on that host, drain it from the pool, and build timelines from seq/trace_id instead of cross-host wall clocks."
