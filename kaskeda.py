import json
import pandas as pd
from collections import Counter

keys = [
    'author', 'created_utc',
    'domain', 'id', 'num_comments',
    'score', 'subreddit', 'title',
    'url'
]

def open_submissions(file):
    submissions = []
    # This is over eight million lines!
    with open(file) as f:
        for line in f:
            try:
                l = json.loads(line)
                submissions.append({k: l[k] for k in keys})
            except:
                # TODO: Why are some submissions not working?
                # Not a huge deal: we can ignore them for now,
                # but this would be good to fix later.
                pass
    return submissions

# TODO: Get this from an argument.
submissions = open_submissions("./data/RS_2016-10")
print(len(submissions))

t = pd.DataFrame(submissions)
print(t[t["domain"] == 'rt.com']["domain"].count())
print(t[t["domain"] == 'economist.com']["domain"].count())
print(t[t["domain"] == 'aljazeera.com']["domain"].count())
print(t["domain"].value_counts()[0:100])
