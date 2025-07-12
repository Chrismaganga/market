from django.contrib import admin
from .models import Category, CategoryAttribute


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'sort_order', 'listings_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Settings', {
            'fields': ('is_active', 'sort_order')
        }),
    )
    
    def listings_count(self, obj):
        return obj.get_listings_count()
    listings_count.short_description = 'Listings Count'


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'attribute_type', 'is_required', 'is_filterable', 'is_searchable', 'sort_order']
    list_filter = ['attribute_type', 'is_required', 'is_filterable', 'is_searchable', 'category']
    search_fields = ['name', 'category__name']
    ordering = ['category', 'sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'attribute_type')
        }),
        ('Settings', {
            'fields': ('is_required', 'is_filterable', 'is_searchable', 'sort_order')
        }),
        ('Options (for select/multiselect)', {
            'fields': ('options',),
            'description': 'Enter options as a JSON array, e.g., ["Option 1", "Option 2"]'
        }),
    ) 