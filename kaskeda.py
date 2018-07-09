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
from functools import partial

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
    
class RedditProcessor:
    def __init__(self):
        self.store = []

    def filter(self, line):
        return True

    def process(self, obj):
        try:
            self.store.append(obj["subreddit"])
        except:
            pass

class RTCounter(RedditProcessor):
    def filter(self, line):
        #return True
        return 'domain":"rt.com' in str(line)

class BBCCounter(RedditProcessor):
    def filter(self, line):
        #return True
        return 'domain":"bbc.com' in str(line)

class RedditScraper:
    process_list = []
    def __init__(self, processes=1, path='./data'):
        self._pool = Pool(processes)
        self.path = path
        #self._process_list = []
        self._files = self._get_files()

    def _get_files(self):
        files = []
        for file in os.listdir(self.path):
            # Use join to get full file path.
            location = os.path.join(self.path, file)
            size = os.path.getsize(location)
            files.append((size, location))
        files.sort(key=lambda s: s[0], reverse=True)
        return [x[1] for x in files]
            
    def add_process(self, p):
        # TODO: Check here if `p` is a class?
        RedditScraper.process_list.append(p)

    def _run(f, processes):
        classes = [x() for x in processes]
        i = 10000000
        for line in itertools.islice(open_compressed(f), i):
            for c in classes:
                if c.filter(line):
                    try:
                        c.process(json.loads(line))
                    except:
                        pass
        return classes

    def run(self):
        p = self._pool.map(
            partial(RedditScraper._run, processes=RedditScraper.process_list),
            self._files
        )
        # flatten
        results = [list() for _ in range(len(RedditScraper.process_list))]
        for p_results in p:
            for i, r in enumerate(p_results):
                results[i] += r.store
        return results

if __name__ == '__main__':
    scraper = RedditScraper(processes=64, path='/scratch/ccolglaz/data/')
    scraper.add_process(RTCounter)
    scraper.add_process(BBCCounter)
    results = scraper.run()
    print(Counter(results[0]).most_common(10))
    print(Counter(results[1]).most_common(10))
    
