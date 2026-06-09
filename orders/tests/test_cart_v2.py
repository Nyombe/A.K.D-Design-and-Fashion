from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Category, Product, ProductVariantAttribute, ProductVariantOption, ProductVariantValue
from orders.models import Cart, CartItem, Order, OrderItem
from decimal import Decimal

User = get_user_model()


class CartV2APITests(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Testpassword123!"
        )
        
        # Create category & product
        self.category = Category.objects.create(name="Clothing", description="Apparel")
        
        self.product = Product.objects.create(
            name="Designer Shirt",
            description="High-end designer shirt",
            category=self.category,
            price=Decimal("120.00"),
            stock=20,
            sku="SHR-001"
        )
        
        # Create variant configuration
        self.size_attr = ProductVariantAttribute.objects.create(name="size", display_name="Size")
        self.size_m = ProductVariantOption.objects.create(attribute=self.size_attr, value="Medium", display_value="M")
        
        self.variant = ProductVariantValue.objects.create(
            product=self.product,
            sku="SHR-001-M",
            attributes={"size": "Medium"},
            price_override=Decimal("130.00"),
            stock=10,
            is_active=True
        )

        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_get_or_create_cart(self):
        """Test active cart retrieval or automatic creation."""
        url = reverse('cart-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertTrue(response.data['is_active'])
        self.assertEqual(response.data['item_count'], 0)

    def test_add_item_to_cart_without_variant(self):
        """Test adding a product to cart without variant selections."""
        url = reverse('cart-list')
        # First retrieve the cart to know the ID
        response = self.client.get(url)
        cart_id = response.data['id']
        
        # Add item
        add_url = reverse('cart-add-item', kwargs={'pk': cart_id})
        data = {
            "product_id": self.product.id,
            "quantity": 2
        }
        add_response = self.client.post(add_url, data, format='json')
        self.assertEqual(add_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(add_response.data['quantity'], 2)
        self.assertEqual(float(add_response.data['price']), 120.00)
        self.assertEqual(float(add_response.data['total_price']), 240.00)
        self.assertIsNone(add_response.data['variant'])

    def test_add_item_to_cart_with_variant(self):
        """Test adding a product to cart with variant selections."""
        url = reverse('cart-list')
        response = self.client.get(url)
        cart_id = response.data['id']
        
        # Add item with variant
        add_url = reverse('cart-add-item', kwargs={'pk': cart_id})
        data = {
            "product_id": self.product.id,
            "quantity": 1,
            "variant_selections": {"size": "Medium"}
        }
        add_response = self.client.post(add_url, data, format='json')
        self.assertEqual(add_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(add_response.data['quantity'], 1)
        self.assertEqual(float(add_response.data['price']), 130.00) # Overridden price
        self.assertEqual(add_response.data['variant'], self.variant.id)
        self.assertEqual(add_response.data['variant_selections'], {"size": "Medium"})

    def test_update_cart_item(self):
        """Test updating item quantity in cart."""
        url = reverse('cart-list')
        response = self.client.get(url)
        cart_id = response.data['id']
        
        # First add an item
        add_url = reverse('cart-add-item', kwargs={'pk': cart_id})
        data = {"product_id": self.product.id, "quantity": 1}
        add_response = self.client.post(add_url, data, format='json')
        cart_item_id = add_response.data['id']
        
        # Update quantity
        update_url = reverse('cart-update-item', kwargs={'pk': cart_id})
        update_data = {
            "cart_item_id": cart_item_id,
            "quantity": 3
        }
        update_response = self.client.patch(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['quantity'], 3)
        self.assertEqual(float(update_response.data['total_price']), 360.00)

        # Update to 0 should remove item
        update_data["quantity"] = 0
        remove_response = self.client.patch(update_url, update_data, format='json')
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertEqual(remove_response.data['message'], 'Item removed from cart')

    def test_remove_cart_item(self):
        """Test removing an item from the cart."""
        url = reverse('cart-list')
        response = self.client.get(url)
        cart_id = response.data['id']
        
        # First add an item
        add_url = reverse('cart-add-item', kwargs={'pk': cart_id})
        data = {"product_id": self.product.id, "quantity": 2}
        add_response = self.client.post(add_url, data, format='json')
        cart_item_id = add_response.data['id']
        
        # Remove item
        remove_url = reverse('cart-remove-item', kwargs={'pk': cart_id})
        remove_response = self.client.delete(remove_url, {"cart_item_id": cart_item_id}, format='json')
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertEqual(remove_response.data['message'], 'Item removed from cart')

    def test_clear_cart(self):
        """Test clearing the cart."""
        url = reverse('cart-list')
        response = self.client.get(url)
        cart_id = response.data['id']
        
        # Add two different items
        add_url = reverse('cart-add-item', kwargs={'pk': cart_id})
        self.client.post(add_url, {"product_id": self.product.id, "quantity": 2}, format='json')
        
        # Clear cart
        clear_url = reverse('cart-clear', kwargs={'pk': cart_id})
        clear_response = self.client.post(clear_url)
        self.assertEqual(clear_response.status_code, status.HTTP_200_OK)
        
        # Verify cart items count is 0
        get_response = self.client.get(url)
        self.assertEqual(get_response.data['item_count'], 0)

    def test_convert_anonymous_cart(self):
        """Test converting/merging local storage anonymous cart with DB cart."""
        url = reverse('cart-list')
        response = self.client.get(url)
        cart_id = response.data['id']
        
        convert_url = reverse('cart-convert-anonymous', kwargs={'pk': cart_id})
        data = {
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 3,
                    "variant_selections": {"size": "Medium"}
                }
            ]
        }
        convert_response = self.client.post(convert_url, data, format='json')
        self.assertEqual(convert_response.status_code, status.HTTP_200_OK)
        
        # Verify item added with correct quantity & variant
        self.assertEqual(convert_response.data['item_count'], 1)
        item = convert_response.data['items'][0]
        self.assertEqual(item['quantity'], 3)
        self.assertEqual(item['variant'], self.variant.id)


class GuestCheckoutTests(APITestCase):
    def setUp(self):
        # Create category & product
        self.category = Category.objects.create(name="Footwear", description="Shoes")
        self.product = Product.objects.create(
            name="Classic Boots",
            description="Very nice leather boots",
            category=self.category,
            price=Decimal("90.00"),
            stock=15,
            sku="BTS-001"
        )
        
        # We do NOT authenticate the user, as we are testing Guest Checkout.

    def test_guest_checkout_success(self):
        """Test guest checkout endpoint with valid anonymous cart data."""
        url = reverse('guest-checkout')
        data = {
            "email": "guest@example.com",
            "full_name": "John Doe",
            "delivery_address": "123 Fashion Blvd",
            "delivery_location": "New York",
            "delivery_phone": "+1234567890",
            "cart_items": {
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": 1
                    }
                ]
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_id', response.data)
        self.assertIn('order_number', response.data)
        self.assertEqual(response.data['payment_status'], 'pending')
        
        # Verify order exists in DB
        order = Order.objects.get(id=response.data['order_id'])
        self.assertEqual(order.email, "guest@example.com")
        self.assertEqual(order.full_name, "John Doe")
        self.assertEqual(order.delivery_location, "New York")
        self.assertEqual(order.subtotal, Decimal("90.00"))
        
        # Check shipping calculation (< 100 subtotal should charge 9.99 shipping)
        self.assertEqual(order.shipping_cost, Decimal("9.99"))
        self.assertEqual(order.tax_amount, Decimal("7.20"))  # 90 * 0.08 = 7.20
        self.assertEqual(order.total_amount, Decimal("107.19"))
        
        # Verify order items are created
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.unit_price, Decimal("90.00"))

    def test_guest_checkout_free_shipping(self):
        """Test guest checkout free shipping calculation (subtotal >= 100)."""
        url = reverse('guest-checkout')
        data = {
            "email": "guest2@example.com",
            "full_name": "Jane Smith",
            "delivery_address": "456 Luxury St",
            "delivery_location": "Juba",
            "delivery_phone": "+256781398233",
            "cart_items": {
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": 2 # 90.00 * 2 = 180.00 subtotal (>= 100)
                    }
                ]
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order = Order.objects.get(id=response.data['order_id'])
        self.assertEqual(order.shipping_cost, Decimal("0.00"))
        self.assertEqual(order.tax_amount, Decimal("14.40"))  # 180 * 0.08 = 14.4
        self.assertEqual(order.total_amount, Decimal("194.40"))
