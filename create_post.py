import os
import subprocess
from datetime import datetime

# ==========================================
# 설정
# ==========================================
BLOG_REPO_PATH = r"C:\Python_Note\kangtaeminwork-web.github.io"
POSTS_DIR = os.path.join(BLOG_REPO_PATH, "_posts")

# ==========================================
# 1단계: 포스트 내용 입력받기
# ==========================================
print("=" * 40)
print("  블로그 포스트 자동 생성기")
print("=" * 40)

title = input("\n포스트 제목을 입력하세요: ")
category = input("카테고리를 입력하세요 (예: python, git, etc): ")
DRAFT_PATH = os.path.join(os.path.dirname(__file__), "draft.md")

if not os.path.exists(DRAFT_PATH):
    print("❌ draft.md 파일이 없습니다. 먼저 만들어주세요!")
    exit()

with open(DRAFT_PATH, "r", encoding="utf-8") as f:
    content = f.read()

print("✅ draft.md 읽기 완료!")

# ==========================================
# 2단계: 파일명 & 날짜 자동 생성
# ==========================================
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")           # 예: 2025-01-15
time_str = today.strftime("%Y-%m-%d %H:%M:%S")  # 예: 2025-01-15 14:30:00

# 제목을 파일명으로 변환 (공백 → 하이픈, 소문자)
slug = input("파일명을 영어로 입력하세요 (예: jwt-auth): ")
title_slug = slug.lower().replace(" ", "-")
filename = f"{date_str}-{title_slug}.md"
filepath = os.path.join(POSTS_DIR, filename)

# ==========================================
# 3단계: 마크다운 파일 내용 작성
# ==========================================
post_content = f"""---
layout: post
title: "{title}"
date: {time_str} +0900
categories: {category}
---

{content}
"""

# ==========================================
# 4단계: 파일 저장
# ==========================================
# _posts 폴더가 없으면 생성
os.makedirs(POSTS_DIR, exist_ok=True)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"\n✅ 파일 생성 완료: {filename}")

# ==========================================
# 5단계: git add → commit → push 자동화
# ==========================================
print("\n📤 GitHub에 업로드 중...")

# subprocess: 파이썬에서 터미널 명령어 실행하는 모듈
# cwd = 명령어를 실행할 폴더 위치 지정
commands = [
    ["git", "pull"],
    ["git", "add", "."],
    ["git", "commit", "-m", f"Add post: {title}"],
    ["git", "push"],
]

for cmd in commands:
    print(f"  실행: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=BLOG_REPO_PATH,   # 블로그 저장소 폴더에서 실행
        capture_output=True,  # 출력 결과를 변수에 저장
        text=True,            # 결과를 문자열로 변환
        encoding="utf-8"
    )
    
    if result.returncode == 0:  # returncode 0 = 성공
        print(f"  ✅ 성공")
    else:
        print(f"  ❌ 실패: {result.stderr}")
        break

print("\n🎉 완료! 블로그에서 확인하세요:")
print(f"   https://kangtaeminwork-web.github.io")