from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderItem, Product
from .serializers import CreateOrderSerializer, OrderSerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start is not None:
                queryset = queryset.filter(created_at__date__gte=parsed_start)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end is not None:
                queryset = queryset.filter(created_at__date__lte=parsed_end)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = Product.objects.get(pk=data['product_id'])
        quantity = data['quantity']

        if product.stock < quantity:
            return Response(
                {'detail': 'Insufficient stock for the requested quantity.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            status=Order.STATUS_PENDING,
            customer_email=data.get('customer_email', ''),
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_order=product.price,
        )

        product.stock = product.stock - quantity
        product.save()

        output = OrderSerializer(order, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.status = Order.STATUS_CANCELLED
        order.save()

        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        order.status = Order.STATUS_SHIPPED
        order.save()

        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
