from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# user 
class UserBase (BaseModel) : 
    username : str
    wallet_address : str

class UserCreate (UserBase) : 
    pass

class UserInDB (BaseModel) : 
    id : int
    username : str
    wallet_address : str

    class Config : 
        model_config = {
            "from_attributes" : True
        }

class UserAuth (BaseModel) : 
    username : str
    wallet_address : str
    

# paper
class PaperBase (BaseModel) : 
    title : str
    summary : str
    ipfs_hash : str

class PaperCreate (PaperBase) : 
    owner_id : int

class PaperInDB (PaperBase) : 
    id : int
    owner_id : int
    tx_hash : Optional[str] = None
    created_at : datetime

    class Config : 
        model_config = {
            "from_attributes" : True
        }


# comment
class CommentBase (BaseModel) : 
    ipfs_hash : str

class CommentCreate (CommentBase) : 
    paper_id : int
    reviewer_id : int

class CommentInDB (CommentBase) : 
    id : int
    paper_id : int
    reviewer_id : int
    tx_hash : Optional[str] = None
    created_at : datetime

    class Config : 
        model_config = {
            "from_attributes" : True
        }


# reviewer assign
class ReviewerInDB (BaseModel) : 
    id : int
    paper_id : int
    user_id : int
    assigned_at : datetime

    class Config : 
        model_config = {
            "from_attributes" : True
        }

class PaperDetail (PaperInDB) : 
    reviewers : List[ReviewerInDB] = []

    model_config = {
        "from_attributes" : True
    }