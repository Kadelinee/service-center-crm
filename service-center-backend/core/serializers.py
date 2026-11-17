from rest_framework import serializers
from .models import Clients, Services, Orders, OrderServices
from django.utils import timezone
from django.db import transaction

class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=100)

    phone = serializers.RegexField(
        regex=r'^\+?[0-9]{10,13}$',
        max_length=20,
        error_messages={
            'invalid': 'Введіть коректний номер телефону.'
        }
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = Clients
        fields = [
            'client_id',
            'full_name',
            'phone',
            'email',
            'notes',
            'created_at'
        ]
        read_only_fields = ['client_id', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )

    duration_minutes = serializers.IntegerField(min_value=1)

    class Meta:
        model = Services
        fields = [
            'service_id',
            'category',
            'name',
            'description',
            'price',
            'duration_minutes',
            'is_active'
        ]
        read_only_fields = ['service_id']


class OrderSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Clients.objects.all()
    )

    user = serializers.PrimaryKeyRelatedField(
        queryset=Orders._meta.get_field('user').remote_field.model.objects.all(),
        required=False,
        allow_null=True
    )

    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Services.objects.all(),
        write_only=True,
        required=False
    )

    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        write_only=True
    )

    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=False
    )

    class Meta:
        model = Orders
        fields = [
            'order_id',
            'client',
            'user',
            'order_date',
            'scheduled_at',
            'status',
            'total_price',
            'service_id',
            'quantity'
        ]
        read_only_fields = ['order_id']

    def validate_status(self, value):
        allowed_statuses = [
            'new',
            'confirmed',
            'in_progress',
            'completed',
            'cancelled'
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                'Некоректний статус замовлення.'
            )

        return value

    def validate(self, attrs):
        if self.instance is None and 'service_id' not in attrs:
            raise serializers.ValidationError({
                'service_id': 'Оберіть послугу.'
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        service = validated_data.pop('service_id')
        quantity = validated_data.pop('quantity', 1)

        price = service.price
        total = price * quantity

        validated_data['total_price'] = total

        if validated_data.get('order_date') is None:
            validated_data['order_date'] = timezone.now()

        if not validated_data.get('status'):
            validated_data['status'] = 'new'
        order = Orders.objects.create(**validated_data)

        OrderServices.objects.create(
            order=order,
            service=service,
            quantity=quantity,
            price_at_order=price
        )

        return order


class OrderServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(
        source='service.name',
        read_only=True
    )

    class Meta:
        model = OrderServices
        fields = [
            'order_service_id',
            'order',
            'service',
            'service_name',
            'quantity',
            'price_at_order'
        ]
        read_only_fields = fields
