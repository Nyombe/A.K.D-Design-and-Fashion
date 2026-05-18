# Generated manually for A.K.D marketplace scaling
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_pricehistory_change_reason'),
        ('users', '0003_customuser_role_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='users.vendor'),
        ),
    ]
