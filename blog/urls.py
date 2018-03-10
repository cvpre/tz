from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('new-category/', views.new_category, name='new_category'),
    path('category/<int:category_pk>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:category_pk>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:category_pk>/topics/', views.topics, name='topics'),
    path('category/<int:category_pk>/new-topic/', views.new_topic, name='new_topic'),
    path('category/<int:category_pk>/topic/<int:topic_pk>/', views.TopicPosts.as_view(), name='topic_posts'),
    path('category/<int:category_pk>/topic/<int:topic_pk>/reply/', views.reply_topic, name='reply_topic'),
    path('category/<int:category_pk>/topic/<int:topic_pk>/edit/',
         views.edit_topic, name='edit_topic'),
    path('category/<int:category_pk>/topic/<int:topic_pk>/posts/<int:post_pk>)/edit/',
         views.edit_post, name='edit_post'),
    path('category/<int:category_pk>/topic/<int:topic_pk>/posts/<int:post_pk>)/delete/',
         views.delete_post, name='delete_post'),
    path('category/<int:category_pk>/topic/<int:topic_pk>/delete/',
         views.delete_topic, name='delete_topic'),
]
