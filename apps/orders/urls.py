from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_orders, name='my_orders'),

    path('create/<int:tier_id>/', views.create_order, name='create_order'),

    # Specific actions FIRST
    path('<int:pk>/accept/', views.accept_order, name='accept_order'),
    path('<int:pk>/deliver/', views.deliver_order, name='deliver_order'),
    path('<int:pk>/approve/', views.approve_order, name='approve_order'),

    # General detail LAST
    path('<int:pk>/', views.order_detail, name='order_detail'),
]