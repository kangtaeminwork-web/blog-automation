import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts")

posts = response.json()

# print("총 포스트 수:", len(posts))
# 앞에 3개만 출력
for post in posts:
    print("---")
    idBox = post["id"]
    if idBox < 6 :
        title = post["title"]
        print(f"{idBox}번 포스트 제목: ({title})")
    else:
        break
