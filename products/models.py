from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import BaseModel


class Category(BaseModel):
    """Product category model."""
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    """Product model with comprehensive fields for e-commerce."""
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    vendor = models.ForeignKey('users.Vendor', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text='Leave empty if no discount'
    )
    
    # Stock management
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10)
    
    # Product details
    sku = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=200, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=255, blank=True)
    
    # Ratings
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), ])
    num_ratings = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Tracking
    views = models.IntegerField(default=0)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Fashion & Care Details (for high-end e-commerce)
    care_instructions = models.TextField(
        blank=True,
        help_text="E.g., 'Hand wash in cold water. Do not bleach. Air dry.'"
    )
    material_composition = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON format: {'cotton': 80, 'polyester': 20}"
    )
    fit_guide = models.TextField(
        blank=True,
        help_text="Description of how the garment fits (e.g., 'True to size', 'Runs small')"
    )
    style_tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags like ['minimalist', 'bohemian', 'luxury', 'sustainable']"
    )
    occasion = models.CharField(
        max_length=50,
        choices=[
            ('casual', 'Casual'),
            ('formal', 'Formal'),
            ('evening', 'Evening'),
            ('resort', 'Resort'),
            ('active', 'Active'),
            ('workwear', 'Workwear'),
            ('party', 'Party'),
        ],
        blank=True
    )
    season = models.JSONField(
        default=list,
        blank=True,
        help_text="Seasons: ['spring', 'summer', 'fall', 'winter']"
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def clean(self):
        """Validate product data."""
        super().clean()
        
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({
                'discount_price': 'Discount price must be less than regular price.'
            })

        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative.'})

    def get_display_price(self):
        """Get the price to display (discount price if available)."""
        return self.discount_price if self.discount_price else self.price

    def get_discount_percentage(self):
        """Calculate discount percentage."""
        if self.discount_price and self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 2)
        return 0

    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock > 0

    def is_low_stock(self):
        """Check if product is running low on stock."""
        return self.stock > 0 and self.stock <= self.low_stock_threshold

    def update_rating(self, new_rating, user_id=None):
        """Update product rating."""
        if 0 <= new_rating <= 5:
            avg_rating = ((self.rating * self.num_ratings) + new_rating) / (self.num_ratings + 1)
            self.rating = round(avg_rating, 2)
            self.num_ratings += 1
            self.save()

    def get_variants_summary(self):
        """Get a summary of available variants for this product."""
        if not self.variant_values.exists():
            return None
        
        variants_dict = {}
        for variant_value in self.variant_values.filter(is_active=True):
            for attr_name, attr_value in variant_value.attributes.items():
                if attr_name not in variants_dict:
                    variants_dict[attr_name] = set()
                variants_dict[attr_name].add(attr_value)
        
        return {k: sorted(list(v)) for k, v in variants_dict.items()}

    def has_variants(self):
        """Check if product has variants."""
        return self.variant_values.filter(is_active=True).exists()

    def get_available_variant_for(self, variant_selections):
        """
        Get a specific variant based on attribute selections.
        Args:
            variant_selections: dict like {'size': 'Medium', 'color': 'Blue'}
        Returns:
            ProductVariantValue or None
        """
        try:
            return self.variant_values.get(
                attributes=variant_selections,
                is_active=True
            )
        except self.variant_values.model.DoesNotExist:
            return None

    def get_json_ld_schema(self, request=None):
        """
        Generate JSON-LD structured data for Search Engine Optimization (AEO).
        Enables proper indexing by AI agents (Gemini, ChatGPT, Perplexity).
        """
        import json
        from django.urls import reverse
        from django.utils import timezone
        
        # Build absolute URL
        if request:
            absolute_url = request.build_absolute_uri(self.get_absolute_url())
        else:
            absolute_url = self.get_absolute_url()
        
        # Get primary image
        primary_image = self.images.filter(is_primary=True).first() or self.images.first()
        image_url = primary_image.image.url if primary_image and primary_image.image else None
        
        # Build availability status
        availability = "https://schema.org/InStock" if self.is_in_stock() else "https://schema.org/OutOfStock"
        
        # Build price currency object
        price_obj = {
            "@type": "PriceSpecification",
            "price": str(self.get_display_price()),
            "priceCurrency": "USD"
        }
        
        # Add discount price if available
        offers = {
            "@type": "Offer",
            "url": absolute_url,
            "availability": availability,
            "price": str(self.get_display_price()),
            "priceCurrency": "USD"
        }
        
        # Build review aggregation
        review_aggregate = {
            "@type": "AggregateRating",
            "ratingValue": str(self.rating),
            "reviewCount": self.num_ratings
        } if self.rating > 0 else None
        
        # Build material composition
        material_info = []
        if self.material_composition:
            for material, percentage in self.material_composition.items():
                material_info.append(f"{material} {percentage}%")
        
        # Main JSON-LD object
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": self.name,
            "description": self.description,
            "brand": {
                "@type": "Brand",
                "name": self.brand or "A.K.D Fashion"
            },
            "sku": self.sku,
            "category": self.category.name,
            "url": absolute_url,
            "offers": offers,
        }
        
        # Add image
        if image_url:
            schema["image"] = image_url
        
        # Add rating
        if review_aggregate:
            schema["aggregateRating"] = review_aggregate
        
        # Add material composition
        if material_info:
            schema["material"] = ", ".join(material_info)
        
        # Add care instructions
        if self.care_instructions:
            schema["careInstructions"] = self.care_instructions
        
        # Add style tags (for AI understanding)
        if self.style_tags:
            schema["keywords"] = ", ".join(self.style_tags) if isinstance(self.style_tags, list) else self.style_tags
        
        # Add occasion
        if self.occasion:
            schema["occasion"] = self.occasion
        
        return schema

    def get_json_ld_schema_script(self, request=None):
        """
        Get JSON-LD schema as a script tag string.
        """
        import json
        schema = self.get_json_ld_schema(request)
        return json.dumps(schema)

    def get_ai_recommendations(self, limit=4):
        """
        Get AI-powered "Complete the Look" recommendations.
        Uses relevance scoring to surface best matches.
        """
        recommendations = ProductRecommendation.objects.filter(
            source_product=self,
            is_active=True
        ).select_related('recommended_product').order_by(
            '-relevance_score'
        )[:limit]
        
        return [rec.recommended_product for rec in recommendations]

    def get_recommendations(self, limit=6):
        """
        Get recommended products based on collaborative filtering (co-purchases).
        Falls back to category-based recommendations if not enough purchase data.
        """
        from orders.models import OrderItem
        from django.db.models import Count
        
        # Find order IDs that contain this product
        order_ids = OrderItem.objects.filter(product=self).values_list('order_id', flat=True)
        
        # Find other products in those same orders, ordered by frequency
        recommended = Product.objects.filter(
            order_items__order_id__in=order_ids,
            is_active=True
        ).exclude(
            id=self.id
        ).annotate(
            purchase_count=Count('id')
        ).order_by('-purchase_count')[:limit]

        
        # Convert to list to work with it safely and efficiently
        recommended_list = list(recommended)
        
        # If we don't have enough recommendations, pad with products from the same category
        if len(recommended_list) < limit:
            needed = limit - len(recommended_list)
            recommended_ids = [p.id for p in recommended_list] + [self.id]
            
            fallback = Product.objects.filter(
                category=self.category,
                is_active=True
            ).exclude(
                id__in=recommended_ids
            ).order_by('-views', '-rating')[:needed]
            
            recommended_list.extend(list(fallback))
            
        return recommended_list


class ProductImage(BaseModel):
    """Product image model for multiple images per product."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    from core.validators import validate_image_file

    image = models.ImageField(
        upload_to='products/', 
        blank=True, 
        null=True, 
        max_length=255,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']),
            validate_image_file,
        ]
    )
    image_url = models.URLField(max_length=500, blank=True, help_text='Optional: Use if not uploading an image file.')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def clean(self):
        super().clean()
        # Ensure either image or image_url is provided
        if not self.image and not self.image_url:
            raise ValidationError('Either an image file or image URL must be provided.')
        # Limit image file size (e.g., 5MB)
        if self.image:
            if self.image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large (max 5MB).')
            
            # Basic MIME type check using extension if magic not available
            # For a more robust check, you'd use 'python-magic' or similar
            ext = self.image.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                raise ValidationError(f'Unsupported file extension: {ext}')

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class PriceHistory(BaseModel):
    """Track price changes for products over time."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    change_reason = models.CharField(
        max_length=255,
        blank=True,
        choices=[
            ('initial', 'Initial Price'),
            ('promotion', 'Promotion'),
            ('discount', 'Discount'),
            ('price_adjustment', 'Price Adjustment'),
            ('market_change', 'Market Change'),
            ('sales_event', 'Sales Event'),
            ('other', 'Other'),
        ]
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Price History'
        verbose_name_plural = 'Price Histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f"{self.product.name}: {self.old_price} → {self.new_price}"

    def get_price_change(self):
        """Get the price change amount."""
        return self.new_price - self.old_price

    def get_price_change_percentage(self):
        """Get the percentage change."""
        if self.old_price != 0:
            change = ((self.new_price - self.old_price) / self.old_price) * 100
            return round(change, 2)
        return 0


class ProductReview(BaseModel):
    """Customer reviews for products."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product
        indexes = [
            models.Index(fields=['product', 'is_approved']),
        ]

    def __str__(self):
        return f"Review of {self.product.name} by {self.user.email}"


# ============================================================================
# SIGNALS
# ============================================================================

# ============================================================================
# FASHION VARIANT MODELS (Size, Color, Material Support)
# ============================================================================

class ProductVariantAttribute(BaseModel):
    """Variant attribute types (e.g., Size, Color, Material)."""
    
    ATTRIBUTE_TYPES = [
        ('size', 'Size'),
        ('color', 'Color'),
        ('material', 'Material'),
        ('fit', 'Fit'),
        ('pattern', 'Pattern'),
    ]
    
    name = models.CharField(max_length=100, choices=ATTRIBUTE_TYPES, unique=True)
    display_name = models.CharField(max_length=100)  # e.g., "Size", "Colour", "Material"
    
    class Meta:
        verbose_name = 'Product Variant Attribute'
        verbose_name_plural = 'Product Variant Attributes'
    
    def __str__(self):
        return self.display_name


class ProductVariantOption(BaseModel):
    """Options for variant attributes (e.g., S, M, L for Size)."""
    
    attribute = models.ForeignKey(ProductVariantAttribute, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=100)  # e.g., "Small", "Medium", "Large"
    display_value = models.CharField(max_length=100)  # e.g., "S", "M", "L"
    order = models.IntegerField(default=0)
    hex_value = models.CharField(
        max_length=7, 
        blank=True, 
        help_text="For color variants, the hex color code (e.g., #FF5733)"
    )
    
    class Meta:
        verbose_name = 'Product Variant Option'
        verbose_name_plural = 'Product Variant Options'
        ordering = ['order', 'value']
        unique_together = ('attribute', 'value')
    
    def __str__(self):
        return f"{self.attribute.display_name}: {self.display_value}"


class ProductVariantValue(BaseModel):
    """Individual SKU variant (combination of attribute values)."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant_values')
    sku = models.CharField(max_length=100, unique=True)
    attributes = models.JSONField(
        default=dict,
        help_text="JSON format: {'size': 'Small', 'color': 'Red', 'material': 'Cotton'}"
    )
    
    # Pricing
    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Leave blank to use product base price"
    )
    
    # Stock
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Images
    image = models.ImageField(
        upload_to='product_variants/',
        blank=True,
        null=True,
        help_text="Optional variant-specific image"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Product Variant Value'
        verbose_name_plural = 'Product Variant Values'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        attrs_str = ', '.join([f"{k}={v}" for k, v in self.attributes.items()])
        return f"{self.product.name} - {attrs_str}"
    
    def get_price(self):
        """Get price for this variant (override or base)."""
        return self.price_override if self.price_override else self.product.get_display_price()
    
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock > 0


# ============================================================================
# PRODUCT RECOMMENDATION & AI STYLIST ENGINE
# ============================================================================

class ProductRecommendation(BaseModel):
    """AI-powered recommendations for "Complete the Look" features."""
    
    RECOMMENDATION_TYPES = [
        ('completes_look', 'Completes the Look'),
        ('pairs_well', 'Pairs Well With'),
        ('trending_together', 'Trending Together'),
        ('similar_style', 'Similar Style'),
        ('accessory_match', 'Accessory Match'),
        ('seasonal', 'Seasonal Recommendation'),
    ]
    
    source_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='outgoing_recommendations'
    )
    recommended_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='incoming_recommendations'
    )
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    
    # AI/ML relevance
    relevance_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), ]
    )  # 0.0 to 1.0
    reason = models.TextField(
        blank=True,
        help_text="Why these products work together (e.g., 'Complements the dress color')"
    )
    
    # Engagement
    click_through_count = models.IntegerField(default=0)
    conversion_count = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Product Recommendation'
        verbose_name_plural = 'Product Recommendations'
        ordering = ['-relevance_score']
        unique_together = ('source_product', 'recommended_product', 'recommendation_type')
        indexes = [
            models.Index(fields=['source_product', 'is_active']),
            models.Index(fields=['-relevance_score']),
        ]
    
    def __str__(self):
        return f"{self.source_product.name} → {self.recommended_product.name} ({self.recommendation_type})"
    
    def get_conversion_rate(self):
        """Calculate conversion rate for this recommendation."""
        if self.click_through_count == 0:
            return 0
        return round((self.conversion_count / self.click_through_count) * 100, 2)


# ============================================================================
# ENHANCED PRODUCT MODEL FOR JSON-LD / AEO
# ============================================================================

# Note: Add these fields to the Product model using migration:
# - care_instructions (TextField, blank=True)
# - material_composition (JSONField, default=dict)
# - fit_guide (TextField, blank=True)
# - style_tags (JSONField, default=list)
# - occasion (CharField with choices)
# - season (JSONField for multiple seasons)


# ============================================================================
# SIGNALS
# ============================================================================

@receiver(post_save, sender=Product)
def track_price_change(sender, instance, created, **kwargs):
    """Signal to track price changes in history."""
    if created:
        try:
            PriceHistory.objects.create(
                product=instance,
                old_price=instance.price,
                new_price=instance.price,
                change_reason='initial',
                notes='Product created'
            )
        except Exception as e:
            print(f"Error creating initial price history: {e}")
