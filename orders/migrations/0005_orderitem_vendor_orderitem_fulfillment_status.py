# Generated manually for A.K.D marketplace scaling
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_order_shipping_address_and_more'),
        ('users', '0003_customuser_role_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='users.vendor'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='fulfillment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
