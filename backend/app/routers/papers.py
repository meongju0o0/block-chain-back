from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_database
from ..ipfs import ipfs_client
from ..blockchain import blockchain_client

# Prefix correctly set
router = APIRouter(prefix="/api/v1/papers", tags=["papers"])

@router.post("/", response_model=schemas.PaperDetail, status_code=status.HTTP_201_CREATED)
async def create_paper(
    owner_id: int = Form(...),
    title: str = Form(...),
    summary: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_database)
):
    file_bytes = await file.read()
    ipfs_hash = ipfs_client.upload_file(file_bytes, file.filename)

    paper_in = schemas.PaperCreate(
        ipfs_hash=ipfs_hash,
        owner_id=owner_id,
        title=title,
        summary=summary,
    )
    db_paper = crud.create_paper(db, paper_in)

    user = crud.get_user(db, owner_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found User")

    try:
        tx_hash = blockchain_client.submit_paper(
            paper_id=db_paper.id,
            submitter_wallet=user.wallet_address,
            ipfs_hash=ipfs_hash
        )
        db_paper = crud.update_paper_tx_hash(db, db_paper.id, tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"등록 실패 :: {str(e)}")

    assigned = crud.assign_reviewers(db, db_paper.id, num_reviewers=3)
    db_paper.reviewers = assigned
    return db_paper

@router.get("/{paper_id}", response_model=schemas.PaperDetail)
def get_paper_detail(paper_id: int, db: Session = Depends(get_database)):
    paper = crud.get_paper(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Not found paper")

    reviewers = crud.get_reviewers_of_paper(db, paper_id)
    paper.reviewers = reviewers
    return paper

@router.get("/", response_model=List[schemas.PaperDetail])
def list_papers(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    papers = crud.get_all_papers(db, skip=skip, limit=limit)
    for p in papers:
        p.reviewers = crud.get_reviewers_of_paper(db, p.id)
    return papers
