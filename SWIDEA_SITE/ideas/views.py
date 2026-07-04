from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import DevTool, Idea
from .forms import DevToolForm, IdeaForm

def main(request):
    sort = request.GET.get('sort', 'id_desc')
    ideas = Idea.objects.all()

    if sort == 'star':
        ideas = ideas.order_by('-interest', '-created_at', '-id')
    elif sort == 'name':
        ideas = ideas.order_by('title', 'id')
    elif sort == 'id_asc':
        ideas = ideas.order_by('created_at', 'id')
    elif sort == 'id_desc':
        ideas = ideas.order_by('-created_at', '-id')
    else:
        sort = 'id_desc'
        ideas = ideas.order_by('-created_at', '-id')

    return render(request, 'ideas/main.html', {
        'ideas': ideas,
        'current_sort': sort,
    })

def interest_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'plus':
            idea.interest += 1
            idea.save(update_fields=['interest'])
        elif action == 'minus' and idea.interest > 0:
            idea.interest -= 1
            idea.save(update_fields=['interest'])

    sort = request.GET.get('sort', 'id_desc')
    return redirect(f"{reverse('ideas:main')}?sort={sort}")

# 2. 아이디어 등록
def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save()
            return redirect('ideas:idea_detail', pk=idea.pk)
    else:
        form = IdeaForm()
    return render(request, 'ideas/idea_create.html', {'form': form})

# 3. 아이디어 상세
def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    return render(request, 'ideas/idea_detail.html', {'idea': idea})

# 4. 아이디어 수정
def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            form.save()
            return redirect('ideas:idea_detail', pk=idea.pk)
    else:
        form = IdeaForm(instance=idea)
        
    return render(request, 'ideas/idea_update.html', {'form': form, 'idea': idea})

# 아이디어 삭제
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == 'POST':
        idea.delete()
        return redirect('ideas:main') 
    return redirect('ideas:idea_detail', pk=pk)

# 5. 개발툴 목록 조회
def devtool_list(request):
    devtools = DevTool.objects.all()
    return render(request, 'ideas/devtool_list.html', {'devtools': devtools})

# 6. 개발툴 등록
def devtool_create(request):
    if request.method == 'POST':
        form = DevToolForm(request.POST)
        if form.is_valid():
            devtool = form.save()
            return redirect('ideas:devtool_detail', pk=devtool.pk)
    else:
        form = DevToolForm()
    return render(request, 'ideas/devtool_create.html', {'form': form})

# 7. 개발툴 상세 페이지
def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    related_ideas = Idea.objects.filter(devtool=devtool)
    return render(request, 'ideas/devtool_detail.html', {
        'devtool': devtool,
        'related_ideas': related_ideas
    })

# 8. 개발툴 수정 페이지
def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    
    if request.method == 'POST':
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid():
            form.save()
            return redirect('ideas:devtool_detail', pk=devtool.pk)
    else:
        form = DevToolForm(instance=devtool)
        
    return render(request, 'ideas/devtool_update.html', {'form': form, 'devtool': devtool})

# 추가: 개발툴 삭제 기능
def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == 'POST':
        devtool.delete()
        return redirect('ideas:devtool_list')
    return redirect('ideas:devtool_detail', pk=pk)

