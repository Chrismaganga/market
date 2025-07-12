from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('tree/', views.CategoryTreeView.as_view(), name='category-tree'),
    path('<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('<slug:slug>/children/', views.CategoryChildrenView.as_view(), name='category-children'),
    path('<slug:slug>/attributes/', views.CategoryAttributeListView.as_view(), name='category-attributes'),
] 