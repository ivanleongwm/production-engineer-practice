# Interview Commands Cheat Sheet

Useful shell commands for Production Engineer log investigations. All examples assume you are in `js_pe_debug_practice/`.

## Discovery

```bash
# List all log files
find logs -type f

# Count lines per log file
wc -l logs/*

# See newest lines quickly
tail -n 100 logs/gateway.log
tail -n 100 logs/system.log
```

## Correlation by order / trace / exec ID

```bash
# Replace O1111 with the order ID from the incident report
grep -Rni "O1111" logs/

# Trace a request across services
grep -Rni "trace_id=T-O1111" logs/

# Follow an execution report
grep -Rni "exec_id=E71111" logs/

# Client-scoped search
grep -Rni "client_id=C1111" logs/
```

## Errors and warnings

```bash
grep -Rni "ERROR\|WARN" logs/

# Service-specific errors
grep -Rni "level=ERROR" logs/gateway.log logs/risk.log logs/system.log
```

## Connectivity / DNS / ports / process

```bash
grep -Rni "dns\|nslookup\|dig\|resolved_ip\|ttl" logs/system.log
grep -Rni "connect_failed\|connection_refused\|tcp_timeout\|ECONNREFUSED" logs/
grep -Rni "port=9001\|port=9100\|not_listening\|ss -lntp" logs/
grep -Rni "firewall\|iptables\|DROP\|deny" logs/system.log
grep -Rni "process_exit\|OOMKilled\|restart" logs/system.log
```

## Queue / consumer lag

```bash
grep -Rni "consumer_lag\|lag_messages\|lag_ms\|queue_depth\|backlog" logs/
grep -Rni "poll_slow\|partition" logs/position.log logs/system.log
```

## Memory / GC / DB pool / disk

```bash
grep -Rni "gc_pause\|rss_mb\|mem_pct\|memory" logs/
grep -Rni "pool_active\|pool_max\|pool_idle\|pool_timeout\|connection_pool" logs/
grep -Rni "disk_full\|no_space_left\|usage_pct=100" logs/
```

## Deploy / config / auth / LB

```bash
grep -Rni "config_deployed\|config_version\|deploy" logs/system.log
grep -Rni "permission_denied\|entitlement\|AUTH" logs/
grep -Rni "loadbalancer\|backend_selected\|gateway-1\|gateway-2" logs/
grep -Rni "vendor_timeout\|refdata\|cache_hit" logs/
```

## Exchange / FIX / clock skew

```bash
grep -Rni "session_down\|sequence_mismatch\|FIX" logs/
grep -Rni "exchange_ack_missing\|no_exchange_ack" logs/
grep -Rni "ntp\|clock_offset\|host_clock_skew" logs/system.log
```

## Timestamp sorting (simple)

```bash
# Sort all lines containing an order ID by timestamp prefix
grep -h "O1111" logs/* | sort

# Extract ts= field and sort (works when ts= is first field)
grep -h "O1111" logs/* | awk '{print}' | sort -t= -k2
```

## less navigation

```bash
less logs/gateway.log
# Inside less:
#   /O1111     search forward
#   ?ERROR     search backward
#   n / N      next/previous match
#   G          go to end
#   g          go to start
#   q          quit
```

## Quick triage workflow

```bash
find logs -type f
grep -Rni "ORDER_ID_FROM_PROMPT" logs/
grep -Rni "ERROR\|WARN" logs/
less logs/gateway.log
less logs/system.log
```

Replace `ORDER_ID_FROM_PROMPT` with the order ID from the scenario file.
