# Generated migration for variant support in cart and orders

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_add_variant_and_recommendation_models'),
        ('orders', '0005_orderitem_vendor_orderitem_fulfillment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variant',
            field=models.ForeignKey(blank=True, help_text='If product has variants, this links to the selected variant', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_items', to='products.productvariantvalue'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='variant_selections',
            field=models.JSONField(blank=True, default=dict, help_text="JSON: {'size': 'Medium', 'color': 'Blue', 'material': 'Cotton'}"),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='variant',
            field=models.ForeignKey(blank=True, help_text='If product has variants, this links to the ordered variant', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='products.productvariantvalue'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='variant_selections',
            field=models.JSONField(blank=True, default=dict, help_text="JSON: {'size': 'Medium', 'color': 'Blue', 'material': 'Cotton'}"),
        ),
    ]
