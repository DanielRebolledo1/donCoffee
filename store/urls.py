from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('categoria/<slug:categoria_slug>/', views.store, name='productos_por_categoria'),
    path('categoria/<slug:categoria_slug>/<slug:producto_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name= 'search'),
    
    path('admin/productos/', views.producto_list, name='producto_list'),
    path('admin/productos/crear/', views.producto_create, name='producto_create'),
    path('admin/productos/editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('admin/productos/eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),
    
] 
