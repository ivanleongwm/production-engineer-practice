from collections import defaultdict, deque

class LoginMonitor:
    def __init__(self, k, window, cooldown):
        self.k = k
        self.window = window
        self.cooldown = cooldown

        self.failed_logins = defaultdict(deque)
        self.last_alert_time = {}
        self.seen_event_ids = set()

    def process_event(self, event_id, user_id, timestamp, success):
        # duplicate event
        if event_id in self.seen_event_ids:
            return False

        self.seen_event_ids.add(event_id)

        # successful login does not count
        if success:
            return False

        # add failed login
        self.failed_logins[user_id].append(timestamp)

        # remove old failures
        while (
            self.failed_logins[user_id]
            and self.failed_logins[user_id][0] < timestamp - self.window
        ):
            self.failed_logins[user_id].popleft()

        # memory cleanup
        if not self.failed_logins[user_id]:
            del self.failed_logins[user_id]
            return False

        # threshold check
        if len(self.failed_logins[user_id]) >= self.k:
            last_alert = self.last_alert_time.get(user_id)

            if last_alert is None or timestamp - last_alert >= self.cooldown:
                self.last_alert_time[user_id] = timestamp
                return True

        return False