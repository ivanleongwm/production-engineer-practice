from login_events_dataset import EVENTS, EDGE_CASE_EVENTS, EXPECTED_ALERTED_USERS_K3_T100
from collections import deque, defaultdict
import csv
import time

def follow_login_events(filename):
    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)

        # Read and clean header
        header = next(reader)
        header = [col.strip() for col in header]

        while True:
            line = file.readline()

            if not line:
                time.sleep(0.1)
                continue

            # Skip blank lines
            if not line.strip():
                continue

            row_values = next(csv.reader([line]))

            # Strip spaces from values
            row_values = [value.strip() for value in row_values]

            # Skip incomplete lines
            if len(row_values) != len(header):
                print("Skipping incomplete/bad line:", line)
                continue

            row = dict(zip(header, row_values))

            user_id = row["user_id"].strip('"')
            timestamp = int(row["timestamp"])
            success = row["success"].lower() == "true"

            yield user_id, timestamp, success


class LoginMonitor:
    def __init__(self, k, window):
        self.k = k
        self.window = window
        self.failed_logins = defaultdict(deque)
        self.alerted = set()


    def process_event(self, user_id, timestamp, success):
        if success:
            return

        # Add failed logins
        self.failed_logins[user_id].append(timestamp)

        # Remove failed logins outside the window
        while self.failed_logins[user_id] and self.failed_logins[user_id][0] < (timestamp - self.window):
            self.failed_logins[user_id].popleft()

        # Count number of failed logins for user_id, alert if > k, check if already alerted if not 
        if len(self.failed_logins[user_id]) >= self.k and user_id not in self.alerted:
            self.alerted.add(user_id)
            return True


    def get_alerted_users(self):
        return self.alerted
    

monitor = LoginMonitor(k=3, window=100)

for user_id, timestamp, success in follow_login_events("login_events.csv"):
    should_alert = monitor.process_event(user_id, timestamp, success)

    if should_alert:
        print(f"ALERT: {user_id} has too many failed logins")

print(monitor.get_alerted_users())