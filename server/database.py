from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

postgresql_url = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(postgresql_url)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
