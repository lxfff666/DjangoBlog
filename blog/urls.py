from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<path:slug>/update/', views.update_post, name='update_post'),
    path('post/<path:slug>/delete/', views.delete_post, name='delete_post'),
    path('post/<path:slug>/', views.post_detail, name='post_detail'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('tag/<str:tag_slug>/', views.tag_posts, name='tag_posts'),
]