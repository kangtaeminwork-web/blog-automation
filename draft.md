백엔드 학습 프로젝트 — 현재 상태 정리
완료한 것

Phase 1: 파이썬 기초
Phase 2 Step 1: requests 라이브러리
Phase 2 Step 2: Git/GitHub
Phase 2 Step 3: GitHub Pages 블로그
Phase 3: 파이썬으로 블로그 포스트 자동 생성
Phase 4: FastAPI CRUD API 만들기
Phase 5: FastAPI JWT 인증 시스템 구현
Phase 6: 관계형 DB 설계 + 권한 처리
Phase 7: 실무 폴더 구조 리팩터링
Phase 8: Render 배포 (https://blog-automation-ie6s.onrender.com)
Phase 9: 환경변수로 시크릿 관리 (.env + Render Environment)
Phase 10: PostgreSQL로 DB 교체 (데이터 영구 저장)


환경 정보

Windows + VS Code
Python 3.14
가상환경: C:\Python_Note\blog-automation\venv
blog-automation 저장소: github.com/kangtaeminwork-web/blog-automation
블로그 저장소: github.com/kangtaeminwork-web/kangtaeminwork-web.github.io
블로그 주소: kangtaeminwork-web.github.io
배포 주소: https://blog-automation-ie6s.onrender.com


Render 환경변수

SECRET_KEY: my-secret-key-change-this-later
DATABASE_URL: postgresql://blog_automation_db_user:oBCoHxwtUkoWshSV0NWJ91EE0fiG2gsE@dpg-d7cad2m7r5hc73fmtd7g-a/blog_automation_db


현재 파일 구조
blog-automation/
├── routers/
│   ├── __init__.py
│   ├── posts.py      ← 포스트 API
│   └── auth.py       ← 회원 API
├── venv/
├── database.py       ← DB 설정 (PostgreSQL)
├── models.py         ← User, Post DB 모델
├── auth.py           ← JWT 인증 로직 (환경변수 사용)
├── main.py           ← 라우터 등록만 담당
├── create_post.py    ← 블로그 포스트 자동 생성
├── render.yaml       ← Render 배포 설정
├── requirements.txt  ← 패키지 목록
├── draft.md          ← 블로그 글 작성용 임시 파일
└── posts.db          ← SQLite DB (더 이상 사용 안 함)

현재 코드
auth.py
pythonfrom datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
database.py
pythonfrom sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
routers/auth.py
pythonfrom fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import UserDB
from database import get_db
from auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(username: str, password: str, email: str, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.username == username).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다")
    user = UserDB(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return {"message": "회원가입 완료!"}

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호 오류")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
routers/posts.py
pythonfrom fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import PostDB, UserDB
from database import get_db
from auth import decode_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다")
    return user

class Post(BaseModel):
    title: str
    content: str

@router.post("/posts")
def create_post(post: Post, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    new_post = PostDB(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostDB).all()

@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    return post

@router.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    existing_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if existing_post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 포스트만 수정할 수 있습니다")
    existing_post.title = post.title
    existing_post.content = post.content
    db.commit()
    db.refresh(existing_post)
    return existing_post

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    existing_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if existing_post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 포스트만 삭제할 수 있습니다")
    db.delete(existing_post)
    db.commit()
    return {"message": f"{post_id}번 포스트가 삭제됐습니다"}
main.py
pythonfrom fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Base, UserDB
from database import engine, get_db
from auth import decode_token
from routers import posts, auth

app = FastAPI()

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

@app.get("/me")
def get_me(current_user: UserDB = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}
render.yaml
yamlservices:
  - type: web
    name: blog-automation
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.14.0

설치된 패키지
bashpip install fastapi uvicorn sqlalchemy
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install bcrypt==4.0.1
pip install python-dotenv
pip install psycopg2-binary

VS Code 켤 때 순서
bashcd C:\Python_Note\blog-automation
.\venv\Scripts\activate
uvicorn main:app --reload

다음 단계 예정
Phase 11 — 프론트엔드 연결
간단한 HTML 페이지 만들어서 로그인/포스트 작성 UI 붙이기