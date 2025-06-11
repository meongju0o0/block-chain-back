from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import papers, comments, users

Base.metadata.create_all(bind = engine)

app = FastAPI(
    title = "PeerReviewChain",
    description = "MVP v0.1.0",
    version = "0.1.0"
)

origins = [
    "http://localhost:3000",  # React 개발서버 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(comments.router)
app.include_router(users.router)

@app.get("/")
def read_root () :
    return {"message" : "PeerReviewChain MVP 서버가 실행 중입니다."}