from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
    )

    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True)
    featured_image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # 直接返回反向解析的URL，让Django自动处理编码
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # 如果slug为空，根据标题生成
        if not self.slug:
            self.slug = self.title
        
        # 检查slug是否已存在（排除当前实例）
        original_slug = self.slug
        counter = 1
        
        while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            # 如果slug已存在，添加随机后缀
            import random
            import string
            random_suffix = ''.join(random.choices(string.digits, k=4))
            self.slug = f"{original_slug}-{random_suffix}"
            counter += 1
            
            # 防止无限循环
            if counter > 10:
                break
        
        super().save(*args, **kwargs)

    def get_related_posts(self):
        """获取相关文章"""
        if self.category:
            return Post.objects.filter(
                category=self.category,
                status='published'
            ).exclude(id=self.id)[:4]
        return Post.objects.filter(
            status='published'
        ).exclude(id=self.id)[:4]

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
