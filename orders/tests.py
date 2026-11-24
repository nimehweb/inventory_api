from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Order, Product


class OrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            name='Wireless Mouse',
            sku='MOU-001',
            stock=10,
            price=Decimal('19.99'),
        )

    def _create_order(self, quantity, customer_email='shopper@example.com'):
        return self.client.post(
            reverse('order-list'),
            {
                'product_id': self.product.id,
                'quantity': quantity,
                'customer_email': customer_email,
            },
            format='json',
        )

    def _cancel_order(self, order_id):
        return self.client.post(
            reverse('order-cancel', args=[order_id]),
            format='json',
        )

    def _ship_order(self, order_id):
        return self.client.post(
            reverse('order-ship', args=[order_id]),
            format='json',
        )

    def test_create_order_success(self):
        response = self._create_order(quantity=3)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 3)

    def test_create_order_insufficient_stock(self):
        response = self._create_order(quantity=50)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_cancel_order_restores_stock(self):
        create_response = self._create_order(quantity=4)
        order_id = create_response.data['id']

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 6)

        cancel_response = self._cancel_order(order_id)
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_cannot_ship_cancelled_order(self):
        create_response = self._create_order(quantity=2)
        order_id = create_response.data['id']

        self._cancel_order(order_id)

        ship_response = self._ship_order(order_id)
        self.assertEqual(ship_response.status_code, status.HTTP_400_BAD_REQUEST)
