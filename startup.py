from EVE import db
from EVE.models import skill

db.create_all()

with open('EVE/skills_test.csv') as f:
    for line in f:
        l = line.split(',')
        s = skill(l[0],l[1],l[2],l[3])
        db.session.add(s)
        db.session.commit()
    