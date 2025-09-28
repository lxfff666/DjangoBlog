from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'post_count', 'comment_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    
    def post_count(self, obj):
        count = obj.posts.count()
        if count > 0:
            return format_html(
                '<a href="/admin/blog/post/?author__id={}" target="_blank">{}</a>',
                obj.id, count
            )
        return count
    post_count.short_description = '文章数量'
    
    def comment_count(self, obj):
        count = obj.comments.count()
        if count > 0:
            return format_html(
                '<a href="/admin/blog/comment/?author__id={}" target="_blank">{}</a>',
                obj.id, count
            )
        return count
    comment_count.short_description = '评论数量'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('posts', 'comments')


# 注销默认的用户管理器
admin.site.unregister(User)
# 注册自定义的用户管理器
admin.site.register(User, UserAdmin)
