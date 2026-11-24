from rest_framework import serializers

from .models import Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'stock', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_sku',
            'quantity',
            'price_at_order',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'customer_email', 'items', 'total']
        read_only_fields = ['status', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    """Payload accepted by ``POST /api/orders/``."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
