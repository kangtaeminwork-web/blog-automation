from fastapi import APIRouter, Depends, HTTPException
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

# 포스트 수정
@router.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    existing_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    # 포스트가 없다면
    if existing_post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    # 작성자와 수정하는 사람이 다르다면
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 포스트만 수정할 수 있습니다")
    existing_post.title = post.title
    existing_post.content = post.content
    db.commit()
    db.refresh(existing_post)
    return existing_post

# 포스트 삭제
@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    existing_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    # 포스트가 없다면
    if existing_post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    # 작성자와 삭제하는 사람이 다르다면
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 포스트만 삭제할 수 있습니다")
    db.delete(existing_post)
    db.commit()
    return {"message": f"{post_id}번 포스트가 삭제됐습니다"}