from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SavingsAccount
from .serializers import SavingsAccountSerializer

class SavingsAccountViewSet(viewsets.ModelViewSet):
    """
    Proporciona operaciones CRUD para las cuentas de ahorro.
    Solo muestra y permite modificar las cuentas del usuario autenticado.
    """
    
    serializer_class = SavingsAccountSerializer
    permission_classes = [IsAuthenticated] # Solo usuarios logueados pueden acceder

    def get_queryset(self):
        """Devuelve solo las cuentas que pertenecen al usuario actual."""
        return SavingsAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Asigna el usuario actual al crear una nueva cuenta."""
        serializer.save(user=self.request.user)