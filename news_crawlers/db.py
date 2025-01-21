from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

engine = create_engine("sqlite:///sqlite.db")
Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    album_release_date = Column(DateTime, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"Post(album_release_date='{self.album_release_date}')"


Base.metadata.create_all(engine)
Session = sessionmaker(engine)


def purge_past_articles() -> None:
    with Session() as session:
        results = session.query(Post).filter(Post.timestamp <= (datetime.now() - timedelta(days=60))).delete(synchronize_session=False)
        print(results)


if __name__ == "__main__":
    purge_past_articles()
