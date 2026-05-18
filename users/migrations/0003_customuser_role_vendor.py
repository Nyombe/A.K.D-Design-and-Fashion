# Generated manually for A.K.D marketplace scaling
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_customuser_city_remove_customuser_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('customer', 'Customer'), ('vendor', 'Vendor/Business'), ('admin', 'Platform Admin')], default='customer', max_length=20),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('shop_name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('description', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, upload_to='vendor_logos/')),
                ('banner', models.ImageField(blank=True, upload_to='vendor_banners/')),
                ('is_active', models.BooleanField(default=False)),
                ('commission_percentage', models.DecimalField(decimal_places=2, default=10.0, max_digits=5)),
                ('stripe_connect_id', models.CharField(blank=True, max_length=100)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to='users.customuser')),
            ],
            options={
                'verbose_name': 'Vendor Profile',
                'verbose_name_plural': 'Vendor Profiles',
            },
        ),
    ]
