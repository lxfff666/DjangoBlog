from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from blog.models import Post, Comment
from .forms import LoginForm, RegistrationForm, UserProfileForm, PasswordChangeForm


def user_login(request):
    """用户登录视图"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{user.username}！')
                
                # 存储用户信息到session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['email'] = user.email
                
                # 获取下一个要跳转的页面
                next_page = request.GET.get('next', 'blog:post_list')
                return redirect(next_page)
            else:
                messages.error(request, '用户名或密码错误！')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """用户登出视图"""
    logout(request)
    messages.success(request, '您已成功登出！')
    return redirect('accounts:login')


def register(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # 创建新用户
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', '')
            )
            
            messages.success(request, '注册成功！请登录。')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """用户个人资料"""
    user = request.user
    # 显示用户的所有文章（包括草稿和已发布）
    user_posts = user.blog_posts.all().order_by('-created_at')
    user_comments = user.comment_set.all()
    
    context = {
        'user': user,
        'user_posts': user_posts,
        'user_comments': user_comments,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """编辑用户资料"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已成功更新！')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user, user=request.user)
    
    context = {
        'form': form,
        'title': '编辑个人资料'
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    """修改密码"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '密码已成功修改！请使用新密码重新登录。')
            return redirect('accounts:login')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': '修改密码'
    }
    return render(request, 'accounts/change_password.html', context)
