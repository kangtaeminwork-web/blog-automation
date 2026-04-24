from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models import Base, UserDB
from database import engine, get_db
from auth import decode_token
from routers import posts, auth, comments
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다")
    return user

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/me")
def get_me(current_user: UserDB = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}