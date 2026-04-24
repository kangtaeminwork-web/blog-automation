import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BLOG_REPO_PATH = r"C:\Python_Note\kangtaeminwork-web.github.io"
POSTS_DIR = os.path.join(BLOG_REPO_PATH, "_posts")
DRAFT_PATH = os.path.join(os.path.dirname(__file__), "draft.md")

print("=" * 40)
print("  블로그 포스트 자동 생성기")
print("=" * 40)

if not os.path.exists(DRAFT_PATH):
    print("❌ draft.md 파일이 없습니다. 먼저 만들어주세요!")
    exit()

with open(DRAFT_PATH, "r", encoding="utf-8") as f:
    final_content = f.read()

print("✅ draft.md 읽기 완료!")

title = input("\n포스트 제목을 입력하세요: ")
category = input("카테고리를 입력하세요 (예: python, git, etc): ")
slug = input("파일명을 영어로 입력하세요 (예: jwt-auth): ")

today = datetime.now()
date_str = today.strftime("%Y-%m-%d")
time_str = today.strftime("%Y-%m-%d %H:%M:%S")
title_slug = slug.lower().replace(" ", "-")
filename = f"{date_str}-{title_slug}.md"
filepath = os.path.join(POSTS_DIR, filename)

post_content = f"""---
layout: post
title: "{title}"
date: {time_str} +0900
categories: {category}
---

{final_content}
"""

os.makedirs(POSTS_DIR, exist_ok=True)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"\n✅ 파일 생성 완료: {filename}")

print("\n📤 GitHub에 업로드 중...")

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
        cwd=BLOG_REPO_PATH,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    if result.returncode == 0:
        print(f"  ✅ 성공")
    else:
        print(f"  ❌ 실패: {result.stderr}")
        break

print("\n🎉 완료! 블로그에서 확인하세요:")
print(f"   https://kangtaeminwork-web.github.io")