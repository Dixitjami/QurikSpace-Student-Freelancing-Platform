from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('freelancer/<int:user_id>/', views.freelancer_profile, name='freelancer_profile'),
    path('client/<int:user_id>/', views.client_profile, name='client_profile'),
    path('portfolio/add/', views.add_portfolio, name='add_portfolio'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-client-profile/', views.edit_client_profile, name='edit_client_profile'),
]
