import json
import pandas as pd
from collections import Counter
import itertools
import os
# Compression utilities.
import lzma
import bz2
# Multiprocessing to run in parallel
from multiprocessing import Pool

keys = [
    'author', 'created_utc',
    'domain', 'id', 'num_comments',
    'score', 'subreddit', 'title',
    'url'
]

def open_compressed(path):
    """
    Given a path, return an opened file using the appropriate compression
    algorithm.
    """
    if path.endswith(".bz2"):
        return bz2.open(path)
    elif path.endswith(".xz"):
        return lzma.open(path)
    return open(path)
    
def open_submissions(file):
    submissions = []
    # This is over eight million lines!
    with open_compressed(file) as f:
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

def test_read(path):
    subs = []
    with open_compressed(path) as f:
        i = 0
        for line in f:
            #i += 1
            try:
                if 'domain":"rt.com' in str(line):
                    l = json.loads(line)
                    #if l['domain'] == 'rt.com':
                    subs.append(l['subreddit'])
            except:
                print(path, line)
                pass
            #if i > 1000000:
            #    break
    return subs

if __name__ == '__main__':
    path = './data/'
    files = []
    for file in os.listdir(path):
        # Use join to get full file path.
        location = os.path.join(path, file)
        size = os.path.getsize(location)
        files.append((size, location))
    files.sort(key=lambda s: s[0], reverse=True)
    files = [x[1] for x in files]
    
    p = Pool(64)
    subs = p.map(test_read, files)
    print(Counter(itertools.chain(*subs)).most_common(100))
