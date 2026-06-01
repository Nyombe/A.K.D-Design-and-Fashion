"""
Enhanced cart serializers with variant support and persistence.
Supports both user carts and anonymous carts via localStorage.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders.models import Cart, CartItem
from products.models import Product, ProductVariantValue

User = get_user_model()


# ============================================================================
# CART ITEM SERIALIZERS
# ============================================================================

class CartItemSimpleSerializer(serializers.ModelSerializer):
    """Simple cart item serializer for cart drawer/popover."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    variant_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'product_name', 'product_slug',
            'product_image', 'variant', 'variant_selections',
            'variant_display', 'quantity', 'price', 'display_price',
            'total_price'
        )
        read_only_fields = ('id', 'price')
    
    def get_product_image(self, obj):
        """Get product primary image."""
        primary = obj.product.images.filter(is_primary=True).first()
        if primary:
            return str(primary.image.url) if primary.image else primary.image_url
        return None
    
    def get_display_price(self, obj):
        return str(obj.price)
    
    def get_total_price(self, obj):
        return str(obj.get_total_price())
    
    def get_variant_display(self, obj):
        """Format variant selections for display."""
        if obj.variant_selections:
            return ' • '.join([f"{k}: {v}" for k, v in obj.variant_selections.items()])
        return None


class CartItemDetailSerializer(serializers.ModelSerializer):
    """Detailed cart item serializer for full cart page."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_images = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    variant_display = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'product_name', 'product_slug',
            'product_description', 'product_images',
            'variant', 'variant_selections', 'variant_display',
            'quantity', 'price', 'display_price', 'total_price',
            'discount_amount', 'available_quantity'
        )
        read_only_fields = ('id', 'price')
    
    def get_product_images(self, obj):
        """Get all product images."""
        images = obj.product.images.all().order_by('order')
        return [
            {
                'url': str(img.image.url) if img.image else img.image_url,
                'alt_text': img.alt_text,
                'is_primary': img.is_primary
            }
            for img in images
        ]
    
    def get_display_price(self, obj):
        return str(obj.price)
    
    def get_total_price(self, obj):
        return str(obj.get_total_price())
    
    def get_discount_amount(self, obj):
        return str(obj.get_discount_amount())
    
    def get_variant_display(self, obj):
        """Format variant selections for display."""
        if obj.variant_selections:
            return {
                'display_text': ' • '.join([f"{k}: {v}" for k, v in obj.variant_selections.items()]),
                'details': obj.variant_selections
            }
        return None
    
    def get_available_quantity(self, obj):
        """Get available quantity for this item."""
        if obj.variant:
            return obj.variant.stock
        return obj.product.stock


# ============================================================================
# CART SERIALIZERS
# ============================================================================

class CartSerializer(serializers.ModelSerializer):
    """Cart serializer with items."""
    
    items = CartItemSimpleSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = (
            'id', 'user', 'items', 'is_active',
            'item_count', 'total_items', 'total_price', 'total_discount'
        )
        read_only_fields = ('id', 'user', 'items')
    
    def get_total_price(self, obj):
        return str(obj.get_total_price())
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    
    def get_total_discount(self, obj):
        return str(obj.get_total_discount())
    
    def get_item_count(self, obj):
        return obj.items.count()


class CartDetailSerializer(serializers.ModelSerializer):
    """Detailed cart serializer for full cart page."""
    
    items = CartItemDetailSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    estimated_tax = serializers.SerializerMethodField()
    estimated_shipping = serializers.SerializerMethodField()
    estimated_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = (
            'id', 'user', 'items', 'is_active',
            'item_count', 'total_items', 'total_price', 'total_discount',
            'subtotal', 'estimated_tax', 'estimated_shipping', 'estimated_total'
        )
        read_only_fields = ('id', 'user', 'items')
    
    def get_total_price(self, obj):
        return str(obj.get_total_price())
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    
    def get_total_discount(self, obj):
        return str(obj.get_total_discount())
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_subtotal(self, obj):
        return str(obj.get_total_price())
    
    def get_estimated_tax(self, obj):
        """Calculate estimated tax (8% for now)."""
        subtotal = float(obj.get_total_price())
        tax = subtotal * 0.08
        return str(round(tax, 2))
    
    def get_estimated_shipping(self, obj):
        """Calculate estimated shipping based on subtotal."""
        subtotal = float(obj.get_total_price())
        if subtotal >= 100:
            return "0.00"  # Free shipping
        return "9.99"
    
    def get_estimated_total(self, obj):
        """Calculate estimated total with tax and shipping."""
        subtotal = float(obj.get_total_price())
        tax = subtotal * 0.08
        shipping = 0 if subtotal >= 100 else 9.99
        total = subtotal + tax + shipping
        return str(round(total, 2))


# ============================================================================
# LOCAL STORAGE PERSISTENCE SERIALIZERS
# ============================================================================

class AnonymousCartItemSerializer(serializers.Serializer):
    """
    Serializer for anonymous cart items stored in localStorage.
    Use this to validate and convert localStorage data to database carts.
    """
    
    product_id = serializers.IntegerField(required=True)
    product_slug = serializers.CharField(required=False, read_only=True)
    quantity = serializers.IntegerField(min_value=1, required=True)
    variant_selections = serializers.JSONField(required=False, default=dict)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    def validate_product_id(self, value):
        """Validate that product exists."""
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or is inactive.")
        return value
    
    def validate(self, data):
        """Validate variant selections if provided."""
        product_id = data.get('product_id')
        variant_selections = data.get('variant_selections', {})
        
        if variant_selections and product_id:
            try:
                product = Product.objects.get(id=product_id)
                # Try to find the variant
                variant = product.get_available_variant_for(variant_selections)
                if not variant:
                    raise serializers.ValidationError(
                        "Selected variant combination not available."
                    )
                if data.get('quantity', 0) > variant.stock:
                    raise serializers.ValidationError(
                        f"Only {variant.stock} items available for this variant."
                    )
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product not found.")
        
        return data


class AnonymousCartSerializer(serializers.Serializer):
    """
    Serializer for anonymous shopping cart stored in localStorage.
    Validates the entire cart before conversion to database cart.
    """
    
    items = AnonymousCartItemSerializer(many=True, required=True)
    created_at = serializers.DateTimeField(required=False)
    
    def validate_items(self, value):
        """Ensure items list is not empty."""
        if not value:
            raise serializers.ValidationError("Cart must contain at least one item.")
        return value


# ============================================================================
# CART OPERATION SERIALIZERS
# ============================================================================

class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding item to cart."""
    
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    variant_selections = serializers.JSONField(required=False, default=dict)
    
    def validate_product_id(self, value):
        """Validate product exists."""
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Product not found or inactive.")
        return value
    
    def validate(self, data):
        """Validate product and variant availability."""
        product = Product.objects.get(id=data['product_id'])
        quantity = data['quantity']
        variant_selections = data.get('variant_selections', {})
        
        if variant_selections:
            variant = product.get_available_variant_for(variant_selections)
            if not variant:
                raise serializers.ValidationError("Selected variant not available.")
            if quantity > variant.stock:
                raise serializers.ValidationError(
                    f"Only {variant.stock} items available for this variant."
                )
        else:
            if quantity > product.stock:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available."
                )
        
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    
    quantity = serializers.IntegerField(min_value=0)  # 0 to remove item
    
    def validate_quantity(self, value):
        """Validate quantity."""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
