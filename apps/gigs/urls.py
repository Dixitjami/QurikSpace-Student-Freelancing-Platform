from django.urls import path
from . import views

urlpatterns = [
    path('', views.gig_list, name='gig_list'),
    path('create/', views.create_gig, name='create_gig'),
    path('<int:pk>/', views.gig_detail, name='gig_detail'),
    path('<int:pk>/edit/', views.edit_gig, name='edit_gig'),
    path('<int:pk>/delete/', views.delete_gig, name='delete_gig'),
]