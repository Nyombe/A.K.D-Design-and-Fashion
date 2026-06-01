"""
Enhanced API views for cart management with variant support and localStorage persistence.
Includes checkout flow and frictionless guest checkout.
"""

from rest_framework import generics, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from orders.models import Cart, CartItem, Order, OrderItem
from orders.serializers_v2 import (
    CartSerializer, CartDetailSerializer, CartItemDetailSerializer,
    AddToCartSerializer, UpdateCartItemSerializer, AnonymousCartSerializer
)
from products.models import Product, ProductVariantValue


# ============================================================================
# CART VIEWS
# ============================================================================

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for shopping cart management with variant support.
    
    Endpoints:
    - GET /carts/  - List user carts
    - GET /carts/{id}/  - Get cart details
    - POST /carts/  - Create new cart
    - POST /carts/{id}/add_item/  - Add item to cart
    - PATCH /carts/{id}/update_item/  - Update cart item
    - DELETE /carts/{id}/remove_item/  - Remove item from cart
    - POST /carts/{id}/clear/  - Clear entire cart
    - POST /carts/{id}/convert_anonymous/  - Convert localStorage cart to DB cart
    """
    
    serializer_class = CartDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get carts for current user."""
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create user's active cart."""
        cart, created = Cart.objects.get_or_create(
            user=self.request.user,
            is_active=True
        )
        return cart
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Add item to cart with optional variant selection.
        
        Request body:
        {
            "product_id": 1,
            "quantity": 2,
            "variant_selections": {"size": "Medium", "color": "Blue"}
        }
        """
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = Product.objects.get(id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']
        variant_selections = serializer.validated_data.get('variant_selections', {})
        
        try:
            with transaction.atomic():
                if variant_selections:
                    variant = product.get_available_variant_for(variant_selections)
                    price = variant.get_price()
                    
                    # Check if item already in cart
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        variant=variant,
                        defaults={
                            'quantity': quantity,
                            'price': price,
                            'variant_selections': variant_selections
                        }
                    )
                    
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.save()
                else:
                    price = product.get_display_price()
                    
                    # Without variants, unique constraint is (cart, product)
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        variant=None,
                        defaults={
                            'quantity': quantity,
                            'price': price
                        }
                    )
                    
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            CartItemDetailSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def update_item(self, request, pk=None):
        """
        Update cart item quantity or remove if quantity=0.
        
        Request body:
        {
            "cart_item_id": 5,
            "quantity": 3
        }
        """
        cart = self.get_object()
        cart_item_id = request.data.get('cart_item_id')
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        
        if quantity == 0:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        else:
            cart_item.quantity = quantity
            cart_item.save()
            return Response(CartItemDetailSerializer(cart_item).data)
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """Remove specific item from cart."""
        cart = self.get_object()
        cart_item_id = request.data.get('cart_item_id')
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear entire cart."""
        cart = self.get_object()
        cart.clear()
        return Response({'message': 'Cart cleared'})
    
    @action(detail=True, methods=['post'])
    def convert_anonymous(self, request, pk=None):
        """
        Convert anonymous cart (from localStorage) to database cart.
        Merges items with existing cart.
        
        Request body:
        {
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "variant_selections": {"size": "M"}
                }
            ]
        }
        """
        cart = self.get_object()
        serializer = AnonymousCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                for item_data in serializer.validated_data['items']:
                    product = Product.objects.get(id=item_data['product_id'])
                    quantity = item_data['quantity']
                    variant_selections = item_data.get('variant_selections', {})
                    
                    if variant_selections:
                        variant = product.get_available_variant_for(variant_selections)
                        price = variant.get_price()
                        
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            product=product,
                            variant=variant,
                            defaults={
                                'quantity': quantity,
                                'price': price,
                                'variant_selections': variant_selections
                            }
                        )
                        
                        if not created:
                            cart_item.quantity += quantity
                            cart_item.save()
                    else:
                        price = product.get_display_price()
                        
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            product=product,
                            variant=None,
                            defaults={
                                'quantity': quantity,
                                'price': price
                            }
                        )
                        
                        if not created:
                            cart_item.quantity += quantity
                            cart_item.save()
        except Exception as e:
            return Response(
                {'error': f'Error converting cart: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            self.get_serializer(cart).data,
            status=status.HTTP_200_OK
        )
    
    def list(self, request, *args, **kwargs):
        """Get user's active cart."""
        cart = self.get_object()
        return Response(self.get_serializer(cart).data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        """Get cart details."""
        cart = self.get_object()
        return Response(self.get_serializer(cart).data)


# ============================================================================
# GUEST CHECKOUT VIEW
# ============================================================================

class GuestCheckoutSerializer(serializers.Serializer):
    """Serializer for guest checkout without login."""
    
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    delivery_address = serializers.CharField(max_length=500, required=True)
    delivery_location = serializers.CharField(max_length=100, required=True)
    delivery_phone = serializers.CharField(max_length=20, required=True)
    cart_items = AnonymousCartSerializer(required=True)


class GuestCheckoutView(generics.GenericAPIView):
    """
    Guest checkout without requiring login.
    Creates a temporary order for checkout processing.
    """
    
    serializer_class = GuestCheckoutSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Create guest order from cart."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Create a temporary user or use guest checkout
                # For now, we'll create a guest order directly
                
                email = serializer.validated_data['email']
                full_name = serializer.validated_data['full_name']
                delivery_address = serializer.validated_data['delivery_address']
                delivery_location = serializer.validated_data['delivery_location']
                delivery_phone = serializer.validated_data['delivery_phone']
                
                # Calculate totals
                subtotal = 0
                order_items_data = []
                
                for item_data in serializer.validated_data['cart_items']['items']:
                    product = Product.objects.get(id=item_data['product_id'])
                    quantity = item_data['quantity']
                    variant_selections = item_data.get('variant_selections', {})
                    
                    if variant_selections:
                        variant = product.get_available_variant_for(variant_selections)
                        price = float(variant.get_price())
                    else:
                        price = float(product.get_display_price())
                    
                    item_total = price * quantity
                    subtotal += item_total
                    
                    order_items_data.append({
                        'product': product,
                        'variant': variant if variant_selections else None,
                        'variant_selections': variant_selections,
                        'quantity': quantity,
                        'unit_price': price
                    })
                
                # Calculate tax and shipping
                tax = subtotal * 0.08
                shipping = 0 if subtotal >= 100 else 9.99
                total = subtotal + tax + shipping
                
                # Create order
                order = Order.objects.create(
                    email=email,
                    full_name=full_name,
                    delivery_address=delivery_address,
                    delivery_location=delivery_location,
                    delivery_phone=delivery_phone,
                    subtotal=subtotal,
                    tax_amount=tax,
                    shipping_cost=shipping,
                    total_amount=total,
                    payment_status='pending',
                    status='pending'
                )
                
                # Create order items
                for item_data in order_items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],
                        variant=item_data['variant'],
                        variant_selections=item_data['variant_selections'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price']
                    )
                
                return Response(
                    {
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'total_amount': str(order.total_amount),
                        'payment_status': order.payment_status,
                        'redirect_to': f'/checkout/payment/{order.id}/'
                    },
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            return Response(
                {'error': f'Checkout failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
