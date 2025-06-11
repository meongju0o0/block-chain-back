from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_database
from ..ipfs import ipfs_client
from ..blockchain import blockchain_client

# Prefix should not end with '/'
router = APIRouter(prefix="/api/v1/comments", tags=["comments"])

@router.post("/", response_model=schemas.CommentInDB, status_code=status.HTTP_201_CREATED)
async def create_comment(
    paper_id: int,
    reviewer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_database)
):
    file_bytes = await file.read()
    ipfs_hash = ipfs_client.upload_file(file_bytes, file.filename)

    comment_in = schemas.CommentCreate(
        paper_id=paper_id,
        reviewer_id=reviewer_id,
        ipfs_hash=ipfs_hash
    )
    db_comment = crud.create_comment(db, comment_in)

    reviewer = db.query(models.Reviewer).filter(models.Reviewer.id == reviewer_id).first()
    if not reviewer:
        raise HTTPException(status_code=404, detail="Not found reviewer")
    user = db.query(models.User).filter(models.User.id == reviewer.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found user")

    try:
        tx_hash = blockchain_client.submit_comment(
            comment_id=db_comment.id,
            paper_id=paper_id,
            reviewer_wallet=user.wallet_address,
            ipfs_hash=ipfs_hash
        )
        db_comment = crud.update_comment_tx_hash(db, db_comment.id, tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"등록 실패 :: {str(e)}")

    return db_comment

@router.get("/paper/{paper_id}", response_model=List[schemas.CommentInDB])
def list_comments_of_paper(paper_id: int, db: Session = Depends(get_database)):
    return crud.get_comments_of_paper(db, paper_id)