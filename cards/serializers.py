# cards/serializers.py
from rest_framework import serializers

from expenses.serializers import ExpenseSerializer
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id', 
            'user', 
            'bank', 
            'card_type', 
            'last_digits', 
            'credit_limit', 
            'cut_off_date', 
            'payment_due_date', 
            'created_at', 
            'icon'
        ]
        read_only_fields = ['id', 'created_at']
 

class CardSerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = "__all__"

