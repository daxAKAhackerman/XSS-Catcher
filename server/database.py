from typing import Annotated, Iterator

from fastapi import Depends
from settings import settings
from sqlmodel import Session, create_engine

engine = create_engine(settings.db_url)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]
