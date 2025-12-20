from rest_framework import serializers
from .models import SavingsAccount

class SavingsAccountSerializer(serializers.ModelSerializer):
    """Serializer para el modelo SavingsAccount."""
    
    class Meta:
        model = SavingsAccount
        # Incluye todos los campos excepto 'user' y 'created_at' 
        # (user se asigna en la vista)
        fields = [
            'id', 
            'name', 
            'initial_amount', 
            'start_date', 
            'annual_rate', 
            'clabe', 
            'card_number',
        ]
        read_only_fields = ['id']