from typing import Annotated, Iterator

from fastapi import Depends
from sqlmodel import Session, create_engine

POSTGRESQL_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(POSTGRESQL_URL)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]
