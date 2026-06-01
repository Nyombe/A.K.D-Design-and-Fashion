"""
Enhanced serializers for variants, recommendations, and JSON-LD schema.
These work alongside the existing serializers for backward compatibility.
"""

from rest_framework import serializers
from products.models import (
    Category, Product, ProductImage, PriceHistory, ProductReview,
    ProductVariantAttribute, ProductVariantOption, ProductVariantValue,
    ProductRecommendation
)


# ============================================================================
# VARIANT SERIALIZERS
# ============================================================================

class ProductVariantOptionSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariantOption."""
    
    attribute_name = serializers.CharField(source='attribute.display_name', read_only=True)
    
    class Meta:
        model = ProductVariantOption
        fields = ('id', 'attribute', 'attribute_name', 'value', 'display_value', 'order', 'hex_value')
        read_only_fields = ('id',)


class ProductVariantAttributeSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariantAttribute."""
    
    options = ProductVariantOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductVariantAttribute
        fields = ('id', 'name', 'display_name', 'options')
        read_only_fields = ('id',)


class ProductVariantValueSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariantValue (individual SKU)."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    display_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariantValue
        fields = (
            'id', 'product', 'product_name', 'sku', 'attributes',
            'price_override', 'display_price', 'stock', 'in_stock',
            'image', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_display_price(self, obj):
        return str(obj.get_price())
    
    def get_in_stock(self, obj):
        return obj.is_in_stock()


# ============================================================================
# RECOMMENDATION SERIALIZERS (AI STYLIST)
# ============================================================================

class ProductRecommendationDetailSerializer(serializers.ModelSerializer):
    """Serializer for ProductRecommendation with full product details."""
    
    source_product_name = serializers.CharField(source='source_product.name', read_only=True)
    recommended_product_name = serializers.CharField(source='recommended_product.name', read_only=True)
    recommended_product = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductRecommendation
        fields = (
            'id', 'source_product', 'source_product_name',
            'recommended_product', 'recommended_product_name',
            'recommendation_type', 'relevance_score', 'reason',
            'click_through_count', 'conversion_count', 'conversion_rate',
            'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_recommended_product(self, obj):
        """Return simplified product details."""
        product = obj.recommended_product
        return {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': str(product.price),
            'display_price': str(product.get_display_price()),
            'image': str(product.images.filter(is_primary=True).first().image.url) if product.images.exists() else None,
            'rating': product.rating
        }
    
    def get_conversion_rate(self, obj):
        return obj.get_conversion_rate()


class ProductRecommendationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ProductRecommendation lists."""
    
    recommended_product_name = serializers.CharField(source='recommended_product.name', read_only=True)
    
    class Meta:
        model = ProductRecommendation
        fields = (
            'id', 'recommendation_type', 'recommended_product',
            'recommended_product_name', 'relevance_score', 'reason'
        )
        read_only_fields = ('id',)


# ============================================================================
# ENHANCED PRODUCT SERIALIZERS WITH VARIANTS & JSON-LD
# ============================================================================

class ProductListSerializerV2(serializers.ModelSerializer):
    """Enhanced product list serializer with variant support."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    display_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    has_variants = serializers.SerializerMethodField()
    variants_summary = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'price', 'discount_price', 'display_price',
            'discount_percentage', 'category', 'category_name', 'primary_image',
            'rating', 'num_ratings', 'stock', 'in_stock', 'is_featured',
            'has_variants', 'variants_summary', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def get_display_price(self, obj):
        return str(obj.get_display_price())

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return {
                'url': str(primary_image.image.url) if primary_image.image else primary_image.image_url,
                'alt_text': primary_image.alt_text
            }
        return None

    def get_in_stock(self, obj):
        return obj.is_in_stock()
    
    def get_has_variants(self, obj):
        return obj.has_variants()
    
    def get_variants_summary(self, obj):
        return obj.get_variants_summary()


class ProductDetailSerializerV2(serializers.ModelSerializer):
    """Enhanced product detail serializer with variants, recommendations, and JSON-LD."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    
    # Variants
    has_variants = serializers.SerializerMethodField()
    variant_values = ProductVariantValueSerializer(many=True, read_only=True)
    variants_summary = serializers.SerializerMethodField()
    
    # AI Recommendations
    ai_recommendations = serializers.SerializerMethodField()
    
    # JSON-LD Schema
    json_ld_schema = serializers.SerializerMethodField()
    
    # Fashion Details
    material_composition = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'discount_price', 'display_price',
            'discount_percentage', 'category', 'category_name', 'sku', 'brand',
            'stock', 'in_stock', 'is_low_stock', 'weight', 'dimensions',
            'rating', 'num_ratings', 'is_featured', 'images',
            'meta_description', 'meta_keywords',
            # Fashion details
            'care_instructions', 'material_composition', 'fit_guide',
            'style_tags', 'occasion', 'season',
            # Variants
            'has_variants', 'variant_values', 'variants_summary',
            # AI & Recommendations
            'ai_recommendations',
            # JSON-LD
            'json_ld_schema',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_display_price(self, obj):
        return str(obj.get_display_price())

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()

    def get_images(self, obj):
        """Return all product images."""
        images = obj.images.all().order_by('order')
        return [
            {
                'id': img.id,
                'url': str(img.image.url) if img.image else img.image_url,
                'alt_text': img.alt_text,
                'is_primary': img.is_primary
            }
            for img in images
        ]

    def get_in_stock(self, obj):
        return obj.is_in_stock()

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()
    
    def get_has_variants(self, obj):
        return obj.has_variants()
    
    def get_variants_summary(self, obj):
        return obj.get_variants_summary()
    
    def get_material_composition(self, obj):
        """Format material composition for display."""
        if obj.material_composition:
            return [
                {'material': material, 'percentage': percentage}
                for material, percentage in obj.material_composition.items()
            ]
        return []
    
    def get_ai_recommendations(self, obj):
        """Get AI-powered 'Complete the Look' recommendations."""
        recommendations = obj.outgoing_recommendations.filter(
            is_active=True
        ).order_by('-relevance_score')[:4]
        return ProductRecommendationDetailSerializer(
            recommendations,
            many=True,
            context=self.context
        ).data
    
    def get_json_ld_schema(self, obj):
        """Get JSON-LD structured data for SEO/AEO."""
        request = self.context.get('request')
        return obj.get_json_ld_schema(request)
