from django.shortcuts import render
from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)

def handler404(request, exception):
    """自定义404错误处理器"""
    from blog.models import Post
    
    # 获取最近的文章用于推荐
    recent_posts = Post.objects.filter(status='published').order_by('-created_at')[:3]
    
    context = {
        'recent_posts': recent_posts,
    }
    
    response = render(request, '404.html', context)
    response.status_code = 404
    return response

def handler500(request):
    """自定义500错误处理器"""
    logger.error(f"500 error occurred for user: {request.user}", exc_info=True)
    
    context = {}
    
    response = render(request, '500.html', context)
    response.status_code = 500
    return response