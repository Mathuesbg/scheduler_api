from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(engine)


def get_session():
    with Session() as session:
        yield session
