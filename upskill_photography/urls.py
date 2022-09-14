from django.urls import path
from upskill_photography import views
app_name = 'upskill_photography'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('discovery/', views.discovery, name='discovery'),
    path('search/', views.search_result, name='search_result'),
    path('account/', views.account, name='account'),
    path('account/change_profile_picture/', views.change_profile_picture, name='change_profile_picture'),
    path('account/uploads/', views.uploads, name='uploads'),
    path('account/uploads/upload/', views.upload, name='upload'),
    path('categories/', views.categories, name='categories'),
    path('categories/<slug:category_name_slug>/', views.show_category, name='show_category'),
    path('user/<str:userprofile_username>/', views.userprofile, name='userprofile'),
    path('user/<str:userprofile_username>/<uuid:picture_id>/', views.picture_view, name='picture_view'),
    
    # Url's used by AJAX requests
    path('like_picture/', views.LikePictureView.as_view(), name='like_picture'),
    path('remove_comment/', views.RemoveCommentView.as_view(), name='remove_comment'),
    path('remove_picture/', views.RemovePictureView.as_view(), name='remove_picture'),
]
