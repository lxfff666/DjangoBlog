"""
# URL configuration for InkRealm Blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# 自定义错误处理器
handler404 = 'DjangoBlog.views.handler404'
handler500 = 'DjangoBlog.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('accounts/', include('accounts.urls')),
]

# 提供媒体文件和静态文件服务
# 注意：在生产环境中，应该使用Web服务器（如Nginx）来提供这些文件

# 在开发环境中提供静态文件和媒体文件服务
# 这样可以确保即使在DEBUG=False的情况下也能正常访问
if settings.DEBUG or getattr(settings, 'DEVELOPMENT_MODE', False):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
