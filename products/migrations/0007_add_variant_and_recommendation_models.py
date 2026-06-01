# Generated migration for product variant system and AI recommendations

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_add_fashion_metadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariantAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(choices=[('size', 'Size'), ('color', 'Color'), ('material', 'Material'), ('fit', 'Fit'), ('pattern', 'Pattern')], max_length=100, unique=True)),
                ('display_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Product Variant Attribute',
                'verbose_name_plural': 'Product Variant Attributes',
            },
        ),
        migrations.CreateModel(
            name='ProductVariantOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(max_length=100)),
                ('display_value', models.CharField(max_length=100)),
                ('order', models.IntegerField(default=0)),
                ('hex_value', models.CharField(blank=True, help_text='For color variants, the hex color code (e.g., #FF5733)', max_length=7)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='products.productvariantattribute')),
            ],
            options={
                'verbose_name': 'Product Variant Option',
                'verbose_name_plural': 'Product Variant Options',
                'ordering': ['order', 'value'],
            },
        ),
        migrations.CreateModel(
            name='ProductVariantValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('attributes', models.JSONField(default=dict, help_text="JSON format: {'size': 'Small', 'color': 'Red', 'material': 'Cotton'}")),
                ('price_override', models.DecimalField(blank=True, decimal_places=2, help_text='Leave blank to use product base price', max_digits=10, null=True)),
                ('stock', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('image', models.ImageField(blank=True, help_text='Optional variant-specific image', null=True, upload_to='product_variants/')),
                ('is_active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_values', to='products.product')),
            ],
            options={
                'verbose_name': 'Product Variant Value',
                'verbose_name_plural': 'Product Variant Values',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('recommendation_type', models.CharField(choices=[('completes_look', 'Completes the Look'), ('pairs_well', 'Pairs Well With'), ('trending_together', 'Trending Together'), ('similar_style', 'Similar Style'), ('accessory_match', 'Accessory Match'), ('seasonal', 'Seasonal Recommendation')], max_length=20)),
                ('relevance_score', models.FloatField(default=0.5, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('reason', models.TextField(blank=True, help_text='Why these products work together (e.g., \'Complements the dress color\')')),
                ('click_through_count', models.IntegerField(default=0)),
                ('conversion_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('recommended_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_recommendations', to='products.product')),
                ('source_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_recommendations', to='products.product')),
            ],
            options={
                'verbose_name': 'Product Recommendation',
                'verbose_name_plural': 'Product Recommendations',
                'ordering': ['-relevance_score'],
            },
        ),
        migrations.AddConstraint(
            model_name='productvariantoption',
            constraint=models.UniqueConstraint(fields=['attribute', 'value'], name='unique_attribute_value'),
        ),
        migrations.AddIndex(
            model_name='productvariantvalue',
            index=models.Index(fields=['product'], name='products_pr_product_idx'),
        ),
        migrations.AddIndex(
            model_name='productvariantvalue',
            index=models.Index(fields=['sku'], name='products_pr_sku_idx'),
        ),
        migrations.AddIndex(
            model_name='productrecommendation',
            index=models.Index(fields=['source_product', 'is_active'], name='products_pr_source_idx'),
        ),
        migrations.AddIndex(
            model_name='productrecommendation',
            index=models.Index(fields=['-relevance_score'], name='products_pr_relevanc_idx'),
        ),
        migrations.AddConstraint(
            model_name='productrecommendation',
            constraint=models.UniqueConstraint(fields=['source_product', 'recommended_product', 'recommendation_type'], name='unique_recommendation'),
        ),
    ]
