from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Form, status
)
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_database
from ..ipfs import ipfs_client
from ..blockchain import blockchain_client

router = APIRouter(prefix="/api/v1/comments", tags=["comments"])


@router.post(
    "/",
    response_model=schemas.CommentInDB,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    paper_id: int = Form(...),
    reviewer_id: int = Form(...),
    content: str = Form(...),                  # 사용자 코멘트
    db: Session = Depends(get_database),
):
    # 1) paper의 ipfs_hash 조회
    paper = crud.get_paper(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Not found paper")
    paper_ipfs = paper.ipfs_hash

    # 2) DB에 댓글 저장
    comment_in = schemas.CommentCreate(
        paper_id=paper_id,
        reviewer_id=reviewer_id,
        content=content,
    )
    db_comment = crud.create_comment(db, comment_in, paper_ipfs)

    # 3) reviewer 유효성 검사
    user = crud.get_user(db, reviewer_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found reviewer")

    # 4) (옵션) 블록체인 전송
    try:
        tx_hash = blockchain_client.submit_comment(
            comment_id=db_comment.id,
            paper_id=paper_id,
            reviewer_wallet=user.wallet_address,
            ipfs_hash=paper_ipfs,
        )
        crud.update_comment_tx_hash(db, db_comment.id, tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"등록 실패 :: {e}")

    return db_comment


@router.get(
    "/paper/{paper_id}",
    response_model=List[schemas.CommentInDB]
)
def list_comments_of_paper(
    paper_id: int,
    db: Session = Depends(get_database)
):
    return crud.get_comments_of_paper(db, paper_id)