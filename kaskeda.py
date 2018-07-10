import json
from collections import Counter
import itertools
import os
# Compression utilities.
import lzma
import bz2
# Multiprocessing to run in parallel
from multiprocessing import Pool
from functools import partial

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

class RedditCounter(RedditProcessor):
    def __init__(self):
        self.store = Counter()

    def process(self, obj):
        try:
            self.store[obj["subreddit"]] += obj["score"]
        except:
            pass
        

class DomainCounter(RedditCounter):
    def __init__(self, domain):
        super().__init__() 
        self.string = 'domain":"{}"'.format(domain)

    def filter(self, line):
        return self.string in str(line)

class SubredditDomainCounter(DomainCounter):
    def __init__(self, sub):
        self.store = Counter()
        self.string = 'subreddit":"{}"'.format(sub)

    def process(self, obj):
        try:
            self.store[obj["domain"]] += 1
        except:
            pass

class StringSearchCounter(RedditCounter):
    def __init__(self, word):
        super().__init__()
        self.string = word

    def filter(self, line):
        return self.string in str(line)

    def process(self, obj):
        try:
            self.store[obj["subreddit"]] += obj["score"]
        except:
            pass

class RedditScraper:
    process_list = []
    def __init__(self, processes=1, path='./data'):
        self._pool = Pool(processes)
        self.path = path
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
        classes = processes #[x() for x in processes]
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
        for i in range(len(results)):
            # TODO: Should this be a function of RedditProcessor instead?
            # That would allow different types of objects to be used.
            results[i] = sum([x[i].store for x in p], Counter())
        return results

if __name__ == '__main__':
    scraper = RedditScraper(processes=64, path='/scratch/ccolglaz/data/')
    scraper.add_process(DomainCounter("rt.com"))
    scraper.add_process(DomainCounter("bbc.com"))
    scraper.add_process(DomainCounter("aljazeera.com"))
    #scraper.add_process(StringSearchCounter("Neil Gorsuch"))
    results = scraper.run()
    for g in range(len(results)):
        for i, (domain, count) in enumerate(results[g].most_common(25)):
            print("{}. {} ({})".format(i + 1, domain, count))
