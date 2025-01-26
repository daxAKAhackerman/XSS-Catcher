import os
from typing import Annotated, Iterator

from fastapi import Depends
from sqlmodel import Session, create_engine


def get_db_url() -> str:
    if os.getenv("TESTING"):
        return "postgresql://testing:testing@localhost:5433/testing"
    else:
        return "postgresql://postgres:postgres@localhost:5432/postgres"


engine = create_engine(get_db_url())


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]
