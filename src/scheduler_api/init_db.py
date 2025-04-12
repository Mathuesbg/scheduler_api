from scheduler_api.database import engine
from scheduler_api.models import Base

Base.metadata.create_all(bind=engine)
