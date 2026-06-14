from collections import deque, defaultdict

class AlertMonitor:
    def __init__(self, k, window, cooldown):
        self.k = k
        self.window = window
        self.errors = defaultdict(deque)
        self.last_alert_time = {}
        self.cooldown = cooldown
        self.alerts = []

    def process_event(self, timestamp, service, level, message):

        if level != "ERROR":
            return False
        
        # if error add to list for service
        self.errors[service].append(timestamp)

        # if more than T seconds, expel from list
        while self.errors[service] and self.errors[service][0] + self.window < timestamp:
            self.errors[service].popleft()
        
        # if more than k error logs, 
        if len(self.errors[service]) > self.k:
            # if beyond cooldown period
            if service not in self.last_alert_time or timestamp - self.last_alert_time[service] >= self.cooldown:
                self.alerts.append((timestamp, service, message))
                self.last_alert_time[service] = timestamp
                return True
        
        return False
            
    def get_alerts(self):
        return self.alerts

events = [
    (100, "risk", "ERROR", "A"),
    (120, "risk", "ERROR", "B"),
    (140, "risk", "ERROR", "C"),
    (160, "risk", "ERROR", "D"),
    (170, "risk", "ERROR", "E"),
    (230, "risk", "ERROR", "F"),
]

monitor = AlertMonitor(k=3, window=100, cooldown=60)

for timestamp, service, level, message in events:
    should_alert = monitor.process_event(timestamp, service, level, message)

    if should_alert:
        print(f"ALERT: service {service} has error message: {message}")

print(monitor.get_alerts())