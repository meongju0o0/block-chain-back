from sqlalchemy.orm import Session
from sqlalchemy import func
import random

from . import models, schemas

# user 
def get_user (db : Session, user_id : int) : 
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_wallet (db : Session, wallet_address : str) : 
    return db.query(models.User).filter(models.User.wallet_address == wallet_address).first()

def create_user (db : Session, user : schemas.UserAuth) : 
    db_user = models.User(username = user.username, wallet_address = user.wallet_address)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username_and_wallet (db : Session, username : str, wallet_address : str) : 
    return (
        db.query(models.User)
        .filter(models.User.username == username)
        .filter(models.User.wallet_address == wallet_address)
        .first()
    )

# paper
def create_paper (db : Session, paper : schemas.PaperCreate) : 
    db_paper = models.Paper(ipfs_hash = paper.ipfs_hash, owner_id = paper.owner_id)
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper

def get_paper (db : Session, paper_id : int) : 
    return db.query(models.Paper).filter(models.Paper.id == paper_id).first()

def get_all_papers (db : Session, skip : int = 0, limit : int = 100) :
    return db.query(models.Paper).offset(skip).limit(limit).all()

def update_paper_tx_hash (db : Session, paper_id : int, tx_hash : str) :
    # 나중에 block 등록 후 hash값 등록
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    paper.tx_hash = tx_hash
    db.commit()
    db.refresh(paper)
    return paper


# reviewer
def assign_reviewers (db : Session, paper_id : int, num_reviewers : int = 3) : 
    paper = get_paper(db, paper_id)

    if not paper : return []

    all_user_ids = [user.id for user in db.query(models.User).filter(models.User.id != paper.owner_id).all()]
    if (len(all_user_ids) <= num_reviewers) : selected = all_user_ids
    else : selected = random.sample(all_user_ids, num_reviewers)

    assigned = []
    for user_id in selected : 
        reviewer = models.Reviewer(paper_id = paper_id, user_id = user_id) 
        db.add(reviewer)
        db.commit()
        db.refresh(reviewer)
        assigned.append(reviewer)
    
    return assigned

def get_reviewers_of_paper (db : Session, paper_id : int) : 
    return db.query(models.Reviewer).filter(models.Reviewer.paper_id == paper_id).all()

# comment
def create_comment (db : Session, comment : schemas.CommentCreate) : 
    db_comment = models.Comment(
        paper_id = comment.paper_id,
        reviewer_id = comment.reviewer_id,
        ipfs_hash = comment.ipfs_hash
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_of_paper (db : Session, paper_id : int) : 
    return db.query(models.Comment).filter(models.Comment.paper_id == paper_id).all()

def update_comment_tx_hash (db : Session, comment_id : int, tx_hash : str) :
    # 나중에 block 등록 후 hash값 등록
    comment = db.query(models.Paper).filter(models.Comment.id == comment_id).first()
    comment.tx_hash = tx_hash
    db.commit()
    db.refresh(comment)
    return comment