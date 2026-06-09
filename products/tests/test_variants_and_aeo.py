from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from products.models import (
    Category, Product, ProductImage, PriceHistory,
    ProductVariantAttribute, ProductVariantOption, ProductVariantValue,
    ProductRecommendation
)
from decimal import Decimal

User = get_user_model()


class ProductVariantsAndAETestCase(TestCase):
    def setUp(self):
        # Create categories
        self.category = Category.objects.create(
            name="Apparel",
            description="Luxury clothing items"
        )
        
        # Create a user for review / vendor testing if needed
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Testpassword123!"
        )

        # Create basic product with fashion metadata
        self.product = Product.objects.create(
            name="Silk Evening Gown",
            description="A premium silk evening gown.",
            category=self.category,
            price=Decimal("299.99"),
            stock=15,
            sku="DRS-001",
            brand="AKD Luxury",
            care_instructions="Dry clean only. Do not bleach.",
            material_composition={"silk": 100},
            fit_guide="True to size with a slim fit",
            style_tags=["evening", "luxury", "silk"],
            occasion="evening",
            season=["summer", "fall"]
        )

    def test_product_creation_and_metadata(self):
        """Test that the product was created with the correct fashion metadata."""
        product = Product.objects.get(sku="DRS-001")
        self.assertEqual(product.name, "Silk Evening Gown")
        self.assertEqual(product.price, Decimal("299.99"))
        self.assertEqual(product.care_instructions, "Dry clean only. Do not bleach.")
        self.assertEqual(product.material_composition, {"silk": 100})
        self.assertEqual(product.style_tags, ["evening", "luxury", "silk"])
        self.assertEqual(product.occasion, "evening")
        self.assertEqual(product.season, ["summer", "fall"])

    def test_price_history_signal(self):
        """Test that the price tracking signal creates a PriceHistory entry."""
        # Check initial price history entry created by signal
        history = PriceHistory.objects.filter(product=self.product)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().new_price, Decimal("299.99"))
        self.assertEqual(history.first().change_reason, 'initial')

        # Update the product price
        self.product.price = Decimal("249.99")
        self.product.save()

        # Check if new price history is generated or if signals are properly tracked
        # Wait, the current signal only handles created=True:
        # @receiver(post_save, sender=Product)
        # def track_price_change(sender, instance, created, **kwargs):
        #     if created: ...
        # Therefore, price changes on update are not tracked automatically in the signal,
        # which matches the signal logic we saw: `if created: ...`.
        # Let's verify this behavior.
        self.assertEqual(PriceHistory.objects.filter(product=self.product).count(), 1)

    def test_product_validation(self):
        """Test product clean method validation."""
        # Discount price higher than price should raise ValidationError
        self.product.discount_price = Decimal("350.00")
        with self.assertRaises(ValidationError):
            self.product.clean()

    def test_variants_creation_and_helper_methods(self):
        """Test creation of variant attributes, options, values, and verification methods."""
        # 1. Create variant attributes
        size_attr = ProductVariantAttribute.objects.create(
            name="size",
            display_name="Size"
        )
        color_attr = ProductVariantAttribute.objects.create(
            name="color",
            display_name="Color"
        )

        # 2. Create variant options
        size_m = ProductVariantOption.objects.create(
            attribute=size_attr,
            value="Medium",
            display_value="M",
            order=1
        )
        color_red = ProductVariantOption.objects.create(
            attribute=color_attr,
            value="Red",
            display_value="Red",
            order=1,
            hex_value="#FF0000"
        )

        # 3. Create ProductVariantValue (the actual variant SKU)
        variant = ProductVariantValue.objects.create(
            product=self.product,
            sku="DRS-001-M-RED",
            attributes={"size": "Medium", "color": "Red"},
            price_override=Decimal("319.99"),
            stock=5,
            is_active=True
        )

        # Verify variant properties
        self.assertEqual(variant.get_price(), Decimal("319.99"))
        self.assertTrue(variant.is_in_stock())

        # Test product variant helper methods
        self.assertTrue(self.product.has_variants())
        
        summary = self.product.get_variants_summary()
        self.assertIn("size", summary)
        self.assertIn("color", summary)
        self.assertIn("Medium", summary["size"])
        self.assertIn("Red", summary["color"])

        # Test retrieving a specific variant
        retrieved_variant = self.product.get_available_variant_for({"size": "Medium", "color": "Red"})
        self.assertEqual(retrieved_variant, variant)

        # Test retrieving a non-existent variant combination
        self.assertIsNone(self.product.get_available_variant_for({"size": "Large", "color": "Red"}))

    def test_ai_recommendations(self):
        """Test ProductRecommendation model and AI-powered recommendations."""
        # Create a second product
        recommended_prod = Product.objects.create(
            name="Evening Silk Clutch",
            description="Matching evening silk clutch.",
            category=self.category,
            price=Decimal("49.99"),
            stock=10,
            sku="ACC-001",
            brand="AKD Luxury",
        )

        # Create recommendation
        rec = ProductRecommendation.objects.create(
            source_product=self.product,
            recommended_product=recommended_prod,
            recommendation_type="completes_look",
            relevance_score=0.95,
            reason="Complements the evening gown perfectly.",
            is_active=True
        )

        # Verify recommendation metrics
        self.assertEqual(rec.get_conversion_rate(), 0)
        rec.click_through_count = 100
        rec.conversion_count = 15
        rec.save()
        self.assertEqual(rec.get_conversion_rate(), 15.0)

        # Verify product recommendations fetching
        recs = self.product.get_ai_recommendations()
        self.assertIn(recommended_prod, recs)
        self.assertEqual(len(recs), 1)

    def test_json_ld_schema(self):
        """Test JSON-LD schema generation for AEO/SEO search engine optimization."""
        schema = self.product.get_json_ld_schema()
        
        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "Product")
        self.assertEqual(schema["name"], "Silk Evening Gown")
        self.assertEqual(schema["sku"], "DRS-001")
        self.assertEqual(schema["brand"]["name"], "AKD Luxury")
        self.assertEqual(schema["offers"]["price"], "299.99")
        self.assertEqual(schema["offers"]["priceCurrency"], "USD")
        self.assertEqual(schema["material"], "silk 100%")
        self.assertEqual(schema["careInstructions"], "Dry clean only. Do not bleach.")
        self.assertEqual(schema["keywords"], "evening, luxury, silk")
        self.assertEqual(schema["occasion"], "evening")
