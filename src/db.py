import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./activities.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    participants = relationship(
        "Participant",
        back_populates="activity",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (UniqueConstraint("email", "activity_id", name="uix_email_activity"),)

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    activity = relationship("Activity", back_populates="participants")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db_session():
    return SessionLocal()


def commit_session(session):
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
