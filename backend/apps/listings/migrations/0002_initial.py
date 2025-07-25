# Generated by Django 4.2.7 on 2025-07-12 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
        ('listings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='listingview',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='viewed_listings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listingreport',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='listings.listing'),
        ),
        migrations.AddField(
            model_name='listingreport',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_filed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listingreport',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_reviewed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='listings.listing'),
        ),
        migrations.AddField(
            model_name='listingfavorite',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='listings.listing'),
        ),
        migrations.AddField(
            model_name='listingfavorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='categories.category'),
        ),
        migrations.AddField(
            model_name='listing',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='listingfavorite',
            unique_together={('user', 'listing')},
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['status', 'is_active'], name='listings_status_195ac5_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['category', 'status'], name='listings_categor_7f7673_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['seller', 'status'], name='listings_seller__9c3ec9_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['price'], name='listings_price_e6fc4f_idx'),
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['created_at'], name='listings_created_ac7d1b_idx'),
        ),
    ]
