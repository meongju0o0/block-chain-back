from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_database

router = APIRouter(prefix = "/api/v1/user", tags = ["users"])

@router.post("/register", response_model = schemas.UserInDB, status_code = status.HTTP_201_CREATED)
def register (user_in : schemas.UserAuth, db : Session = Depends(get_database)) :
    existing = crud.get_user_by_username_and_wallet(db, user_in.username, user_in.wallet_address)
    if existing : raise HTTPException(status_code = 400, detail = "Already Registered User")
    user = crud.create_user(db, user_in)
    return user

@router.post("/login", response_model = schemas.UserInDB)
def login (user_in : schemas.UserAuth, db : Session = Depends(get_database)) :
    user = crud.get_user_by_username_and_wallet(db, user_in.username, user_in.wallet_address)
    if not user : raise HTTPException(status_code = 401, detail = "Not Found User")
    return user