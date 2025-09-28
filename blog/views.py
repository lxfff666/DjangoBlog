from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm


def post_list(request):
    """文章列表视图 - 增强版"""
    # 只显示已发布文章，不显示任何草稿文章
    posts = Post.objects.filter(status='published')
    
    posts = posts.order_by('-created_at')
    
    # 搜索功能
    search_query = request.GET.get('q', '')  # 默认为空字符串而不是None
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # 分类筛选
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page', 1)  # 默认为第1页
    page_obj = paginator.get_page(page_number)
    
    # 获取所有分类用于筛选
    categories = Category.objects.all()
    
    # 获取热门标签 - 只统计已发布文章的标签
    from taggit.models import Tag
    from django.db.models import Count
    from django.contrib.contenttypes.models import ContentType
    
    # 获取所有已发布文章的ID
    published_post_ids = Post.objects.filter(status='published').values_list('id', flat=True)
    
    # 获取Post模型的ContentType
    post_content_type = ContentType.objects.get_for_model(Post)
    
    # 通过TaggedItem中间表来统计标签使用情况
    popular_tags = Tag.objects.filter(
        taggit_taggeditem_items__object_id__in=published_post_ids,
        taggit_taggeditem_items__content_type=post_content_type
    ).annotate(
        post_count=Count('taggit_taggeditem_items')
    ).order_by('-post_count')[:15]
    
    # 获取热门文章（按浏览量排序）
    popular_posts = Post.objects.filter(
        status='published'
    ).order_by('-views')[:5]
    
    # 获取最新评论
    recent_comments = Comment.objects.select_related(
        'author', 'post'
    ).order_by('-created_at')[:5]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'popular_tags': popular_tags,
        'popular_posts': popular_posts,
        'recent_comments': recent_comments,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """文章详情页 - 增强版"""
    # 处理URL编码问题
    from urllib.parse import unquote
    
    # 基础查询：先查找已发布文章
    post = Post.objects.filter(slug=slug, status='published').first()
    
    # 如果没找到，尝试URL解码后的slug
    if not post:
        try:
            decoded_slug = unquote(slug)
            post = Post.objects.filter(slug=decoded_slug, status='published').first()
        except Exception:
            pass
    
    # 如果没找到已发布文章，检查是否是作者访问自己的草稿
    if not post and request.user.is_authenticated:
        post = Post.objects.filter(slug=slug, author=request.user, status='draft').first()
        # 如果还是没找到，尝试解码后的slug
        if not post:
            try:
                decoded_slug = unquote(slug)
                post = Post.objects.filter(slug=decoded_slug, author=request.user, status='draft').first()
            except Exception:
                pass
    
    # 如果还是没找到，返回404
    if not post:
        from django.http import Http404
        raise Http404('文章不存在或无权访问')
    
    # 增加浏览量
    post.increase_views()
    
    # 获取评论
    comments = post.comments.filter(is_approved=True)
    
    # 获取相关文章
    related_posts = post.get_related_posts()
    
    # 处理评论表单
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '评论已提交成功！')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
def create_post(request):
    """写文章页面 - 增强版"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # 如果没有摘要，自动生成
            if not post.excerpt:
                # 从内容中提取纯文本作为摘要
                import re
                from django.utils.html import strip_tags
                content_text = strip_tags(post.content)
                post.excerpt = content_text[:300] if len(content_text) > 300 else content_text
            
            post.save()
            form.save_m2m()  # 保存多对多关系，包括标签
            
            messages.success(request, f'文章《{post.title}》发布成功！')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, '表单验证失败，请检查输入内容')
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form, 
        'title': '发布新文章',
        'is_create': True
    })


@login_required
def update_post(request, slug):
    """修改文章 - 增强版"""
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save()  # 这会保存所有字段，包括多对多关系
            
            messages.success(request, f'文章《{updated_post.title}》更新成功！')
            return redirect('blog:post_detail', slug=updated_post.slug)
        else:
            messages.error(request, '表单验证失败，请检查输入内容')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form, 
        'title': '编辑文章',
        'is_create': False,
        'post': post
    })


@login_required
def delete_post(request, slug):
    """删除文章"""
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '文章删除成功！')
        return redirect('blog:post_list')
    
    return render(request, 'blog/post_delete.html', {'post': post})


@login_required
def delete_comment(request, comment_id):
    """删除评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 只允许评论作者或文章作者删除评论
    if request.user == comment.author or request.user == comment.post.author:
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, '评论删除成功！')
        return redirect('blog:post_detail', slug=post_slug)
    else:
        messages.error(request, '您没有权限删除此评论！')
        return redirect('blog:post_detail', slug=comment.post.slug)


def category_posts(request, category_slug):
    """分类文章列表"""
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status='published')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)  # 默认为第1页
    page_obj = paginator.get_page(page_number)
    
    # 获取侧边栏需要的数据
    categories = Category.objects.all()
    
    # 获取热门标签 - 只统计已发布文章的标签
    from taggit.models import Tag
    from django.db.models import Count
    from django.contrib.contenttypes.models import ContentType
    
    # 获取所有已发布文章的ID
    published_post_ids = Post.objects.filter(status='published').values_list('id', flat=True)
    
    # 获取Post模型的ContentType
    post_content_type = ContentType.objects.get_for_model(Post)
    
    # 通过TaggedItem中间表来统计标签使用情况
    popular_tags = Tag.objects.filter(
        taggit_taggeditem_items__object_id__in=published_post_ids,
        taggit_taggeditem_items__content_type=post_content_type
    ).annotate(
        post_count=Count('taggit_taggeditem_items')
    ).order_by('-post_count')[:15]
    
    # 获取热门文章（按浏览量排序）
    popular_posts = Post.objects.filter(
        status='published'
    ).order_by('-views')[:5]
    
    # 获取最新评论
    recent_comments = Comment.objects.select_related(
        'author', 'post'
    ).order_by('-created_at')[:5]
    
    context = {
        'category': category,
        'posts': posts,  # 添加posts变量用于显示文章总数
        'page_obj': page_obj,
        'categories': categories,
        'popular_tags': popular_tags,
        'popular_posts': popular_posts,
        'recent_comments': recent_comments,
    }
    return render(request, 'blog/category_posts.html', context)


def tag_posts(request, tag_slug):
    """标签文章列表"""
    from taggit.models import Tag
    from django.db.models import Count
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags__in=[tag], status='published')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)  # 默认为第1页
    page_obj = paginator.get_page(page_number)
    
    # 获取侧边栏需要的数据
    categories = Category.objects.all()
    
    # 获取热门标签 - 只统计已发布文章的标签
    from taggit.models import Tag
    from django.db.models import Count
    from django.contrib.contenttypes.models import ContentType
    
    # 获取所有已发布文章的ID
    published_post_ids = Post.objects.filter(status='published').values_list('id', flat=True)
    
    # 获取Post模型的ContentType
    post_content_type = ContentType.objects.get_for_model(Post)
    
    # 通过TaggedItem中间表来统计标签使用情况
    popular_tags = Tag.objects.filter(
        taggit_taggeditem_items__object_id__in=published_post_ids,
        taggit_taggeditem_items__content_type=post_content_type
    ).annotate(
        post_count=Count('taggit_taggeditem_items')
    ).order_by('-post_count')[:15]
    
    # 获取热门文章（按浏览量排序）
    popular_posts = Post.objects.filter(
        status='published'
    ).order_by('-views')[:5]
    
    # 获取最新评论
    recent_comments = Comment.objects.select_related(
        'author', 'post'
    ).order_by('-created_at')[:5]
    
    context = {
        'tag': tag,
        'posts': posts,  # 添加posts变量用于显示文章总数
        'page_obj': page_obj,
        'categories': categories,
        'popular_tags': popular_tags,
        'popular_posts': popular_posts,
        'recent_comments': recent_comments,
    }
    return render(request, 'blog/tag_posts.html', context)
