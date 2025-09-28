from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_at', 'post_count')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = '文章数量'





@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'created_at', 'featured_image_preview')
    list_filter = ('status', 'category', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('内容', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('状态', {
            'fields': ('status',)
        }),

    )
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.featured_image.url
            )
        return "无图片"
    featured_image_preview.short_description = '特色图片'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'post__category')
    search_fields = ('content', 'author__username', 'post__title')
    raw_id_fields = ('post', 'author')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['approve_comments', 'disapprove_comments']
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = '评论内容'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'已批准 {queryset.count()} 条评论')
    approve_comments.short_description = '批准选中的评论'
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'已取消批准 {queryset.count()} 条评论')
    disapprove_comments.short_description = '取消批准选中的评论'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'author')
