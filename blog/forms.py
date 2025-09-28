from django import forms
from .models import Post, Comment
from taggit.forms import TagWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'category', 'tags', 'content', 'excerpt', 'featured_image', 'status', 'allow_comments']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入文章标题'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '留空将自动生成'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={'class': 'form-control', 'placeholder': '请输入标签，用逗号分隔'}),
            'content': forms.Textarea(attrs={'class': 'form-control editor-content', 'rows': 20, 'placeholder': '请输入文章内容...'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '简要描述文章内容（可选）'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'slug': 'URL友好的短名称，建议使用字母、数字和连字符，留空将自动生成',
            'excerpt': '文章摘要，如果不填写将自动截取前300个字符',
            'featured_image': '建议尺寸：800x400像素，支持 JPG、PNG、GIF 格式',
            'tags': '输入相关标签，用逗号分隔，例如：Django, Python, Web开发',
            'status': '草稿状态只有作者可见，已发布状态所有人可见',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 让slug字段可选
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            # 如果标题包含中文，直接使用原标题作为slug，否则使用Django的slugify
            import re
            title = self.cleaned_data['title']
            if re.search(r'[\u4e00-\u9fff]', title):
                # 包含中文，清理特殊字符后使用原标题
                import unicodedata
                # 规范化Unicode字符
                slug = unicodedata.normalize('NFKC', title.strip())
                # 替换URL不友好的特殊字符 - 包括中文标点
                slug = re.sub(r'[:：；!?，。、（）()\s]+', '-', slug)
                slug = re.sub(r'-+', '-', slug)  # 合并多个连字符
                slug = slug.strip('-')  # 去除首尾连字符
            else:
                # 不包含中文，使用Django的slugify
                from django.utils.text import slugify
                slug = slugify(title)
        
        # 清理slug - 去除首尾空格，限制长度
        slug = slug.strip()
        if len(slug) > 200:
            slug = slug[:200].strip()
        
        # 不再检查slug重复，让模型save方法处理
        return slug

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('标题长度至少为5个字符')
        if len(title) > 200:
            raise forms.ValidationError('标题长度不能超过200个字符')
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 10:
            raise forms.ValidationError('文章内容长度至少为10个字符')
        return content


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入您的评论内容...'
            }),
        }
        labels = {
            'content': '评论内容',
        }