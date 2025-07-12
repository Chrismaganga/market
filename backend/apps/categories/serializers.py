from rest_framework import serializers
from .models import Category, CategoryAttribute # type: ignore


class CategoryAttributeSerializer(serializers.ModelSerializer):
    """Serializer for category attributes."""
    
    class Meta:
        model = CategoryAttribute
        fields = [
            'id', 'name', 'attribute_type', 'is_required',
            'is_filterable', 'is_searchable', 'options', 'sort_order'
        ]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    
    children = serializers.SerializerMethodField()
    listings_count = serializers.SerializerMethodField()
    breadcrumb = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'parent', 'is_active', 'sort_order', 'children',
            'listings_count', 'breadcrumb', 'created_at'
        ]
    
    def get_children(self, obj):
        """Get immediate children categories."""
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data
    
    def get_listings_count(self, obj):
        """Get count of active listings in this category."""
        return obj.get_listings_count()
    
    def get_breadcrumb(self, obj):
        """Get breadcrumb path for this category."""
        breadcrumb = obj.get_breadcrumb()
        return [
            {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug
            }
            for cat in breadcrumb
        ]


class CategoryDetailSerializer(CategorySerializer):
    """Detailed serializer for categories with attributes."""
    
    attributes = CategoryAttributeSerializer(many=True, read_only=True)
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['attributes']


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for category tree structure."""
    
    children = serializers.SerializerMethodField()
    listings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'icon', 'children', 'listings_count'
        ]
    
    def get_children(self, obj):
        """Get all children recursively."""
        children = obj.children.filter(is_active=True)
        return CategoryTreeSerializer(children, many=True).data
    
    def get_listings_count(self, obj):
        """Get count of active listings in this category."""
        return obj.get_listings_count() 