from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name= 'payments'),
    path('order_complete/', views.order_complete, name= 'order_complete'),
    
    path('pedidos/', views.pedido_list, name='pedido_list'),
    path('pedidos/<int:pedido_id>/update/', views.pedido_update_estado, name='pedido_update_estado'),
    path('pedidos/<int:pedido_id>/delete/', views.pedido_delete, name='pedido_delete'),
]