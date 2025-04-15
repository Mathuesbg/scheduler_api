from scheduler_api.database import engine  # pragma: no cover
from scheduler_api.models import Base  # pragma: no cover

Base.metadata.create_all(bind=engine)  # pragma: no cover
