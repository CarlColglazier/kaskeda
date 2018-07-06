from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import json
import bz2

from sqlalchemy import func, desc

# TODO: Connect this to a persistent database.
engine = create_engine('sqlite:///:memory:')#, echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
inspector = inspect(engine)

class Submission(Base):
    __tablename__ = 'submissions'

    author = Column(String)
    created_utc = Column(Integer)
    domain = Column(String)
    id = Column(String, primary_key=True)
    num_comments = Column(Integer)
    score = Column(Integer)
    subreddit = Column(String)
    title = Column(String)
    url = Column(String)

session = Session()
session.commit()

Base.metadata.create_all(bind=engine)

def open_submissions(file):
    submissions = []
    i = 0
    # This is over eight million lines!
    with bz2.open(file) as f:
        for line in f:
            i += 1
            if i > 100000:
                break
            submissions.append(line)
    return submissions

# TODO: Get this from an argument.
subs = open_submissions("./data/RS_2016-10.bz2")
print(len(subs))

submissions = []
keys = [x["name"] for x in inspector.get_columns('submissions')]
for s in subs:
    try:
        x1 = json.loads(s)
        x2 = {k: x1[k] for k in keys}
        submissions.append(x2)
    except:
        # TODO: Why are some submissions not working?
        # Not a huge deal: we can ignore them for now,
        # but this would be good to fix later.
        print(s)

session.bulk_insert_mappings(Submission, submissions)
session.commit()

print(session.query(func.count('*')).select_from(Submission).scalar())
print(session.query(Submission).filter(Submission.domain.like('rt.com')).count())
print(session.query(Submission).filter(Submission.domain.like('economist.com')).count())
print(session.query(Submission).filter(Submission.domain.like('aljazeera.com')).count())

# Print out the top domains.
print(
    session.query(Submission.domain, func.count(Submission.domain)
    ).group_by(Submission.domain
    ).order_by('count_1 desc'
    ).limit(100
    ).all()
)
