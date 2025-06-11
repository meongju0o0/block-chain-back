from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone 

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    wallet_address = Column(String, unique=True, nullable=False)

    # Relations
    papers = relationship("Paper", back_populates="owner")
    comments = relationship("Comment", back_populates="reviewer", cascade="all, delete-orphan")
    assigned_reviews = relationship("Reviewer", back_populates="user", cascade="all, delete-orphan")

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    ipfs_hash = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tx_hash = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    owner = relationship("User", back_populates="papers")
    reviewers = relationship("Reviewer", back_populates="paper", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="paper", cascade="all, delete-orphan")

class Reviewer(Base):
    __tablename__ = "reviewers"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    paper = relationship("Paper", back_populates="reviewers")
    user = relationship("User", back_populates="assigned_reviews")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 참조를 users.id로 변경
    ipfs_hash = Column(String, nullable=False)
    tx_hash = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    paper = relationship("Paper", back_populates="comments")
    reviewer = relationship("User", back_populates="comments", foreign_keys=[reviewer_id])
