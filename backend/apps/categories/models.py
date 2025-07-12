from django.db import models
from django.core.validators import FileExtensionValidator


class Category(models.Model):
    """Model for marketplace categories."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(
        upload_to='category_icons/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])]
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/categories/{self.slug}/'
    
    def get_listings_count(self):
        """Get count of active listings in this category."""
        from apps.listings.models import Listing
        return Listing.objects.filter(
            category=self,
            is_active=True,
            status='active'
        ).count()
    
    def get_all_children(self):
        """Get all children categories recursively."""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_all_parents(self):
        """Get all parent categories."""
        parents = []
        parent = self.parent
        while parent:
            parents.append(parent)
            parent = parent.parent
        return parents[::-1]  # Reverse to get root first
    
    def get_breadcrumb(self):
        """Get breadcrumb path for this category."""
        return self.get_all_parents() + [self]


class CategoryAttribute(models.Model):
    """Model for category-specific attributes."""
    
    ATTRIBUTE_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('select', 'Select'),
        ('multiselect', 'Multi-Select'),
        ('date', 'Date'),
    ]
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)  # For select/multiselect
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'category_attributes'
        unique_together = ['category', 'name']
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}" 