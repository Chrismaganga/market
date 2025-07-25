# Generated by Django 4.2.7 on 2025-07-12 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('condition', models.CharField(choices=[('new', 'New'), ('like_new', 'Like New'), ('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], default='good', max_length=20)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('sold', 'Sold'), ('expired', 'Expired'), ('suspended', 'Suspended')], default='draft', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_negotiable', models.BooleanField(default=True)),
                ('contact_phone', models.CharField(blank=True, max_length=17)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('attributes', models.JSONField(blank=True, default=dict)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('favorites_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'listings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListingFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'listing_favorites',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListingImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='listing_images/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('is_primary', models.BooleanField(default=False)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'listing_images',
                'ordering': ['is_primary', 'sort_order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('inappropriate', 'Inappropriate Content'), ('spam', 'Spam'), ('fake', 'Fake Item'), ('scam', 'Scam'), ('duplicate', 'Duplicate Listing'), ('other', 'Other')], max_length=20)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='pending', max_length=20)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'listing_reports',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListingView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='view_logs', to='listings.listing')),
            ],
            options={
                'db_table': 'listing_views',
                'ordering': ['-viewed_at'],
            },
        ),
    ]
