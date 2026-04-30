from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    path('requests/', views.RequestListView.as_view(), name='request-list'),
    path('request/<int:pk>/', views.RequestDetailView.as_view(), name='request-detail'),
    path('request/create/', views.RequestCreateView.as_view(), name='request-create'),
    path('request/<int:pk>/update/', views.RequestUpdateView.as_view(), name='request-update'),
    path('request/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request-delete'),

    path('request/<int:request_id>/make-offer/', views.make_offer, name='make-offer'),
    path('request/<int:request_id>/report/', views.report_request, name='report-request'),
    path('search/', views.search_view, name='search'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),
    path('categories/', views.category_list, name='category-list'),
    path('dashboard/', views.supplier_dashboard, name='supplier-dashboard'),
]