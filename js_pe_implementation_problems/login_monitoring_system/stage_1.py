from login_events_dataset import EVENTS, EDGE_CASE_EVENTS, EXPECTED_ALERTED_USERS_K3_T100

from collections import defaultdict, deque

def failed_logins_within_T_seconds(list_of_events, k, window):

    failed_logins = defaultdict(deque)
    alerted = set()

    for user_id, timestamp, success in list_of_events:
        # successful logins do not count
        if success:
            continue

        # Add failed logins
        failed_logins[user_id].append(timestamp)

        
        # Remove failed logins outside the window
        while failed_logins[user_id] and failed_logins[user_id][0] < (timestamp - window):
            failed_logins[user_id].popleft()

        # Count number of failed logins for user_id, alert if > k
        if len(failed_logins[user_id]) >= k:
            alerted.add(user_id)

    return alerted

print(failed_logins_within_T_seconds(EVENTS, 3, 100))