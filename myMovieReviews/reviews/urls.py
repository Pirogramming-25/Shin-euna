from django.urls import path
from . import views  

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
    path('review/create/', views.review_create, name='review_create'),
    path('review/<int:pk>/update/', views.review_update, name='review_update'),
    path('review/<int:pk>/delete/', views.review_delete, name='review_delete'),
]