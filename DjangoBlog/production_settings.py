"""
墨境Blog - 简化生产环境配置 - 本地开发使用
"""
from .settings import *

# 基础安全配置
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# 使用默认密钥（仅用于本地测试）
SECRET_KEY = 'django-insecure-local-production-key'

# 静态文件配置
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# 媒体文件配置
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# 基本安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'