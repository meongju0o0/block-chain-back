from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User
class UserBase(BaseModel):
    username: str
    wallet_address: str

class UserCreate(UserBase):
    pass

class UserAuth(BaseModel):
    username: str
    wallet_address: str

class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True


# Paper
class PaperBase(BaseModel):
    title: str
    summary: str
    ipfs_hash: str

class PaperCreate(PaperBase):
    owner_id: int

class PaperInDB(PaperBase):
    id: int
    owner_id: int
    tx_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Comment
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    paper_id: int
    reviewer_id: int

class CommentInDB(CommentBase):
    id: int
    paper_id: int
    reviewer_id: int
    ipfs_hash: str               # paper.ipfs_hash
    tx_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True



# Reviewer Assignment
class ReviewerInDB(BaseModel):
    id: int
    paper_id: int
    user_id: int
    assigned_at: datetime

    class Config:
        from_attributes = True

# Paper Detail
class PaperDetail(PaperInDB):
    reviewers: List[ReviewerInDB] = []

    class Config:
        from_attributes = True
