from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, CategoryAttribute
from .serializers import (
    CategorySerializer, CategoryDetailSerializer, CategoryTreeSerializer,
    CategoryAttributeSerializer
)


class CategoryListView(generics.ListAPIView):
    """View for listing all categories."""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategoryDetailView(generics.RetrieveAPIView):
    """View for category details."""
    
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.filter(is_active=True)
    lookup_field = 'slug'


class CategoryTreeView(generics.ListAPIView):
    """View for category tree structure."""
    
    serializer_class = CategoryTreeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent=None)


class CategoryChildrenView(generics.ListAPIView):
    """View for category children."""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            return category.children.filter(is_active=True)
        except Category.DoesNotExist:
            return Category.objects.none()


class CategoryAttributeListView(generics.ListAPIView):
    """View for listing category attributes."""
    
    serializer_class = CategoryAttributeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            return category.attributes.all()
        except Category.DoesNotExist:
            return CategoryAttribute.objects.none() 