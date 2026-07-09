from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post, Like, Comment, Story, StoryImage, Follow
import json

# 로그인
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user, created = User.objects.get_or_create(username=username)
        login(request, user)
        return redirect('feed')
    return render(request, 'instagram/login.html')

# 메인 피드
@login_required
def feed_view(request):
    user = request.user
    following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    
    feed_users = list(following_ids) + [user.id]
    posts = Post.objects.filter(author_id__in=feed_users).order_by('-created_at')
    stories = Story.objects.filter(author_id__in=feed_users).order_by('-created_at')
    
    my_likes = Like.objects.filter(user=user).values_list('post_id', flat=True)

    context = {
        'posts': posts,
        'stories': stories,
        'my_likes': my_likes,
    }
    return render(request, 'instagram/feed.html', context)


# 좋아요
@login_required
def post_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        like_filter = Like.objects.filter(user=request.user, post=post)
        
        if like_filter.exists():
            like_filter.delete()
            liked = False
        else:
            Like.objects.create(user=request.user, post=post)
            liked = True
            
        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count()
        })

# 댓글
@login_required
def comment_create(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        try:
            if request.body:
                data = json.loads(request.body)
                content = data.get('content')
            else:
                content = request.POST.get('content')

            if content:
                comment = Comment.objects.create(
                    post=post,
                    user=request.user, 
                    content=content
                )
                
                return JsonResponse({
                    'status': 'success',
                    'username': comment.user.username, 
                    'content': comment.content,
                    'comment_id': comment.id
                })
            else:
                return JsonResponse({'status': 'fail', 'message': '내용이 없습니다.'}, status=400)
        except (json.JSONDecodeError, AttributeError) as e:
            return JsonResponse({'status': 'fail', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'fail', 'message': '잘못된 요청 방식입니다.'}, status=405)


@login_required
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == 'POST':
        new_content = request.POST.get('content')
        if new_content:
            comment.content = new_content
            comment.save()
            return redirect('feed')
            
    return render(request, 'instagram/comment_form.html', {'comment': comment})


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return redirect('feed')



# 게시글 생성/수정/삭제
@login_required
def post_create(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        content = request.POST.get('content')
        if image:
            Post.objects.create(author=request.user, image=image, content=content)
            return redirect('feed')
    return render(request, 'instagram/post_form.html')

@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.content = request.POST.get('content', post.content)
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        post.save()
        return redirect('feed')
    return render(request, 'instagram/post_form.html', {'post': post})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
    return redirect('feed')

# 유저 검색 및 프로필 상세
@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else []
    return render(request, 'instagram/search.html', {'users': users, 'query': query})

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.order_by('-created_at')
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
    }
    return render(request, 'instagram/profile.html', context)

# 팔로우
@login_required
def user_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        return redirect('user_profile', username=username)
        
    follow_filter = Follow.objects.filter(following=target_user, follower=request.user)
    
    if follow_filter.exists():
        follow_filter.delete()
    else:
        Follow.objects.create(following=target_user, follower=request.user)
        
    return redirect('user_profile', username=username)


# 스토리 생성 및 상세
@login_required
def story_create(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if images:
            story = Story.objects.create(author=request.user)
            for img in images:
                StoryImage.objects.create(story=story, image=img)
            return redirect('feed')
    return render(request, 'instagram/story_form.html')

@login_required
def story_detail(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return render(request, 'instagram/story_detail.html', {'story': story})