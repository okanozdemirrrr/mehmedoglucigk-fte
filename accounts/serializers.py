from rest_framework import serializers

from .models import User, Dealer


class UserSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.name', read_only=True, allow_null=True)
    dealer_code = serializers.CharField(source='dealer.code', read_only=True, allow_null=True)
    dealer_id = serializers.IntegerField(source='dealer.id', read_only=True, allow_null=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 'role_display',
            'is_distributor', 'is_dealer', 'phone',
            'dealer_id', 'dealer_name', 'dealer_code',
        ]
        read_only_fields = fields


class DealerSerializer(serializers.ModelSerializer):
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = Dealer
        fields = [
            'id', 'code', 'name', 'tax_office', 'tax_number',
            'address', 'city', 'district', 'phone', 'email',
            'is_active', 'credit_limit', 'payment_term_days',
            'discount_rate', 'current_balance',
        ]
        read_only_fields = ['id', 'current_balance']

    def get_current_balance(self, obj):
        return obj.get_current_balance()
