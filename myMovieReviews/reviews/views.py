from django.shortcuts import render, get_object_or_404, redirect
from .models import MovieReview

# 1. 리스트 페이지
def review_list(request):
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'title': #제목 오름차순
        reviews = MovieReview.objects.all().order_by('title')
    elif sort_by == 'star': #별점 내림차순
        reviews = MovieReview.objects.all().order_by('-star_rating')
    elif sort_by == 'time': #시간 내림차순
        reviews = MovieReview.objects.all().order_by('-running_time')
    else: #작성일 최신순
        reviews = MovieReview.objects.all().order_by('-created_at')
    return render(request, 'review_list.html', {'reviews': reviews, 'current_sort': sort_by})

# 2. 디테일 페이지
def review_detail(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)
    return render(request, 'review_detail.html', {'review': review})

# 3. 새 리뷰 작성 페이지
def review_create(request):
    if request.method == 'POST':
        MovieReview.objects.create(
            title=request.POST.get('title'),
            opening_year=request.POST.get('opening_year'),
            director=request.POST.get('director'),
            actor=request.POST.get('actor'),
            genre=request.POST.get('genre'),
            star_rating=request.POST.get('star_rating'),
            running_time=request.POST.get('running_time'),
            content=request.POST.get('content')
        )
        return redirect('review_list')
    return render(request, 'review_form.html')

# 4. 리뷰 수정 페이지
def review_update(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)

    if request.method == 'POST':
        review.title = request.POST['title']
        review.opening_year = request.POST['opening_year']
        review.director = request.POST['director']
        review.actor = request.POST['actor']
        review.genre = request.POST['genre']
        review.star_rating = request.POST['star_rating']
        review.running_time = request.POST['running_time']
        review.content = request.POST['content']
        review.save()
        return redirect('review_detail', pk=review.pk)
    return render(request, 'review_form.html', {'review': review})


# 5. 리뷰 삭제 처리
def review_delete(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)
    if request.method == 'POST':
        review.delete()
        return redirect('review_list')
    return redirect('review_detail', pk=review.pk)
