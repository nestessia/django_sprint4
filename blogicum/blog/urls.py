from django.urls import path


from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexList.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetail.as_view(),
         name='post_detail'),
    path('posts/create/', views.PostCreate.as_view(),
         name='create_post'),
    path('posts/<int:pk>/edit/',
         views.PostUpdate.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDelete.as_view(),
         name='delete_post'),
    path('category/<slug:category_slug>/',
         views.CategoryList.as_view(),
         name='category_posts'),
    path('profile/<slug:username>/',
         views.ProfileList.as_view(),
         name='profile'),
    path('edit_profile/', views.ProfileUpdate.as_view(),
         name='edit_profile'),
    path('posts/<int:pk>/comment/',
         views.CommentAdd.as_view(),
         name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:id>/',
         views.CommentUpdate.as_view(),
         name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:id>/',
         views.CommentDelete.as_view(),
         name='delete_comment'),
]
