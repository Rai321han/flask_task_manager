from db.db import engine, Base
from db.models import Task

Base.metadata.create_all(engine)
print("Tables created!")
