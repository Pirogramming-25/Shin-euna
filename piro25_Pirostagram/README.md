## 필수 구현 기능
1. 📙 게시글 기능
- 작성, 수정, 삭제
2. 👍 좋아요 기능
- 좋아요 눌렀을 때 토글 색 변화, 총 개수 표시
3. 💬 댓글 기능	
- 댓글 작성, 수정, 삭제
4. 📜 스토리 기능
- 여러 장의 사진을 스토리로 올릴 수 있는 기능
5. 🔍 유저 검색 기능
- 계정 아이디/이름으로 유저를 검색, 프로필을 열람까지 가능
6. 👬 팔로우 기능
- 팔로우/언팔로우 기능, 팔로우 한 사람의 게시글과 스토리가 내 피드에 노출

## ERD

1. Users
- id(PK), username, name, profile_img

2. Posts
- id(PK), user_id(FK), content, created_at, updated_at, image

3. Likes
- id(PK), post_id(FK), user_id(FK), created_at

4. Comments
- id(PK), post_id(FK), user_id(FK), content, created_at

5. Stories
- id(PK), user_id(FK), created_at
6. Story_Images
- id(PK), story_id(FK), img_url, order_index

7. Follows
- id(PK), follower_id(FK), following_id(FK), created_at


## 실행

**사용자 계정**
- userA

**가상 계정**
- piro_25
- pirogramming
- django_master
- piroing
데모용으로 가상 유저 4명과 게시글 4개를 만들어놨습니다.


## 📁 프로젝트 폴더 구조

```text
📁 피로스타그램 프로젝트
 ├── 📁 instagram_clone         # Django 앱 폴더
 │    ├── 📄 models.py          # Post, Comment, Story, Follow 모델 정의
 │    ├── 📄 views.py           
 │    └── 📄 urls.py          
 ├── 📁 templates               # HTML 템플릿 폴더
 │    └── 📁 instagram
 │         ├── 📄 comment_form.html  # 댓글 수정
 │         ├── 📄 feed.html          # 메인 홈
 │         ├── 📄 login.html         # 로그인 화면
 │         ├── 📄 profile.html       # 프로필 화면
 │         ├── 📄 post_form.html     # 게시글 작성 및 수정 폼
 │         └── 📄 search.html        # 유저 검색 화면
 │         └── 📄 story_detail.html  # 스토리 상세 화면
 │         └── 📄 story_form.html    # 스토리 업로드 화면
 ├── 📁 media                   # 업로드된 이미지 및 데모 이미지 저장소
 ├── 📄 manage.py
 └── 📄 README.md               

