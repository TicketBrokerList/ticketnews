from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

engine = create_engine("sqlite:///sqlite.db")
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)

    site = Column(String)
    url = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    last_modified = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Post(site='{self.site}', url='{self.url}')"


Base.metadata.create_all(engine)
Session = sessionmaker(engine)


def purge_past_articles() -> None:
    with Session() as session:
        results = (
            session.query(Post)
            .filter(Post.timestamp <= (datetime.utcnow() - timedelta(days=60)).strftime("%m-%d-%Y"))
            .delete(synchronize_session=False)
        )
        print(results)


if __name__ == "__main__":
    purge_past_articles()
