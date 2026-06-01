# Generated migration for luxury fashion fields

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_product_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='care_instructions',
            field=models.TextField(blank=True, help_text="E.g., 'Hand wash in cold water. Do not bleach. Air dry.'"),
        ),
        migrations.AddField(
            model_name='product',
            name='material_composition',
            field=models.JSONField(blank=True, default=dict, help_text="JSON format: {'cotton': 80, 'polyester': 20}"),
        ),
        migrations.AddField(
            model_name='product',
            name='fit_guide',
            field=models.TextField(blank=True, help_text="Description of how the garment fits (e.g., 'True to size', 'Runs small')"),
        ),
        migrations.AddField(
            model_name='product',
            name='style_tags',
            field=models.JSONField(blank=True, default=list, help_text="Tags like ['minimalist', 'bohemian', 'luxury', 'sustainable']"),
        ),
        migrations.AddField(
            model_name='product',
            name='occasion',
            field=models.CharField(blank=True, choices=[('casual', 'Casual'), ('formal', 'Formal'), ('evening', 'Evening'), ('resort', 'Resort'), ('active', 'Active'), ('workwear', 'Workwear'), ('party', 'Party')], max_length=50),
        ),
        migrations.AddField(
            model_name='product',
            name='season',
            field=models.JSONField(blank=True, default=list, help_text="Seasons: ['spring', 'summer', 'fall', 'winter']"),
        ),
    ]
