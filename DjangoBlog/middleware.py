from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class BlockViteRequestsMiddleware:
    """阻止Vite客户端请求的自定义中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查请求路径是否包含Vite相关路径
        if '@vite/client' in request.path or 'vite' in request.path.lower():
            logger.info(f"阻止Vite请求: {request.path}")
            # 返回空的JavaScript响应
            response = HttpResponse(
                content='// Vite客户端请求被阻止\nconsole.log("Vite客户端请求被阻止");',
                content_type='application/javascript'
            )
            return response
        
        response = self.get_response(request)
        return response