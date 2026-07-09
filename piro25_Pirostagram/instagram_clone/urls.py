from django.urls import path
from . import views

urlpatterns = [
    # 인증
    path('login/', views.login_view, name='login'),
    
    # 메인 피드
    path('', views.feed_view, name='feed'),
    
    # 게시글
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/update/', views.post_update, name='post_update'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    
    # 좋아요 & 댓글
    path('post/<int:post_id>/like/', views.post_like, name='post_like'),
    path('post/<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:comment_id>/update/', views.comment_update, name='comment_update'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),

    # 스토리
    path('story/create/', views.story_create, name='story_create'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    
    # 검색 및 프로필/팔로우
    path('search/', views.user_search, name='user_search'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/follow/', views.user_follow, name='user_follow'),
]