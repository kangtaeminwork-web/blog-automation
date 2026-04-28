# Phase 14: 댓글 기능 추가 (백엔드 + 프론트엔드)

## 이번 단계에서 한 것
FastAPI 백엔드에 댓글 기능을 추가하고, 프론트엔드 UI까지 연결해서 실제로 동작하는 댓글 시스템을 완성했다.

---

## 1. DB 모델 추가 (models.py)

댓글을 저장할 `CommentDB` 테이블을 추가했다.

```python
class CommentDB(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    author = relationship("UserDB", back_populates="comments")
    post = relationship("PostDB", back_populates="comments")
```

핵심 개념:
- `ForeignKey("users.id")` — 어떤 유저가 작성했는지 연결
- `ForeignKey("posts.id")` — 어떤 포스트에 달린 댓글인지 연결
- `relationship` — 파이썬 코드에서 편하게 연관 데이터에 접근할 수 있게 해줌

---

## 2. 댓글 API 추가 (routers/comments.py)

댓글 작성 / 조회 / 삭제 3가지 엔드포인트를 만들었다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /posts/{post_id}/comments | 댓글 작성 (로그인 필요) |
| GET | /posts/{post_id}/comments | 댓글 목록 조회 |
| DELETE | /posts/{post_id}/comments/{comment_id} | 댓글 삭제 (본인만 가능) |

권한 처리 핵심:
```python
if comment.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="본인 댓글만 삭제할 수 있습니다")
```
403은 "권한 없음"을 의미하는 HTTP 상태코드다.

---

## 3. 프론트엔드 버그 수정 (static/index.html)

댓글 작성 버튼이 클릭이 안 되는 버그가 있었다.

**원인**: HTML 문자열 안에 `onclick="함수(데이터)"` 방식으로 이벤트를 넣었는데, 포스트 내용에 따옴표나 줄바꿈 같은 특수문자가 있으면 HTML이 깨지면서 버튼 이벤트가 통째로 망가졌다.

**해결**: `onclick` 대신 `addEventListener` 방식으로 교체했다.

```javascript
// 기존 (문제 있는 방식)
<button onclick="createComment(${p.id})">댓글 작성</button>

// 수정 (안전한 방식)
<button class="btn-comment-submit" data-post-id="${p.id}">댓글 작성</button>

// JS에서 이벤트 연결
document.querySelectorAll(".btn-comment-submit").forEach(btn => {
    btn.addEventListener("click", () => createComment(btn.dataset.postId));
});
```

`data-*` 속성에 id만 저장하고, JS에서 이벤트를 따로 연결하는 방식이 훨씬 안전하다.

---

## 배포
- Render에 push 한 번으로 자동 배포 완료
- Render가 GitHub 웹훅으로 변경사항을 감지해서 자동으로 서버를 재시작함
- 배포 주소: https://blog-automation-ie6s.onrender.com/static/index.html