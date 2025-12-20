
# cards/serializers.py
from rest_framework import serializers
from .models import  Expense, Installment
from django.db.models import Sum


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ['id', 'month_number', 'amount', 'due_date', 'is_paid']

class ExpenseSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    paid_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    paid_months = serializers.SerializerMethodField()
    remaining_months = serializers.SerializerMethodField()
    class Meta:
        model = Expense
        fields = [
            'id','card','title','amount','is_msi','months','monthly_amount',
            'created_at','is_paid','paid_month','remaining_months',
            'installments','paid_amount','remaining_amount','paid_months'
        ]
        read_only_fields = ['installments','paid_amount','remaining_amount','paid_months','remaining_months']

    def get_paid_amount(self, obj):
        
        res = obj.installments.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
        return float(res)

    def get_remaining_amount(self, obj):
        paid = obj.installments.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
        rem = (obj.amount or 0) - paid
        return float(rem)

    def get_paid_months(self, obj):
        return obj.installments.filter(is_paid=True).count()

    def get_remaining_months(self, obj):
        if not obj.is_msi or not obj.months:
            return 0
        paid = obj.installments.filter(is_paid=True).count()
        return max(0, obj.months - paid)

class FinancialSummarySerializer(serializers.Serializer):
    user_name = serializers.CharField()
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    credit_card_debt = serializers.DecimalField(max_digits=12, decimal_places=2)