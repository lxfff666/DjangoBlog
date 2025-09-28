"""
开发环境URL配置
用于在开发环境中提供静态文件和媒体文件服务
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from . import views

# 基础URL配置
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('accounts/', include('accounts.urls')),
]

# 开发环境静态文件和媒体文件服务
# 注意：在生产环境中，应该使用Web服务器（如Nginx）来提供这些文件
if settings.DEBUG or settings.DEVELOPMENT_MODE:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 自定义错误处理器
handler404 = 'DjangoBlog.views.handler404'
handler500 = 'DjangoBlog.views.handler500'