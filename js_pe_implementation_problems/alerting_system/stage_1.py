# (timestamp, service, level, message)

# Alert if service has more than k error logs within T seconds
# Do not alert service more than once every cooldown seconds

from collections import deque, defaultdict

def process_event(events, k, window, cooldown):
    errors = defaultdict(deque)
    last_alert_time = {}
    alerts = []

    for event in events:
        timestamp, service, level, message = event

        if level != "ERROR":
            continue
        
        # if error add to list for service
        errors[service].append(timestamp)

        # if more than T seconds, expel from list
        while errors[service] and errors[service][0] + window < timestamp:
            errors[service].popleft()
        
        # if more than k error logs, 
        if len(errors[service]) > k:
            # if beyond cooldown period
            if service not in last_alert_time or timestamp - last_alert_time[service] > cooldown:
                alerts.append((timestamp, service, message))
                last_alert_time[service] = timestamp

    return alerts

