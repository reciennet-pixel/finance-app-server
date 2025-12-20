from django.db import models
from django.conf import settings
from decimal import Decimal

class SavingsAccount(models.Model):
    """Modelo para representar una cuenta de ahorro o inversión."""
    
    # Asume que el usuario está autenticado
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_accounts',
        verbose_name="Usuario"
    )
    
    name = models.CharField(max_length=255, verbose_name="Nombre de la Cuenta")
    
    initial_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Monto Inicial"
    )
    
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    
    # Tasa de crecimiento anual (Ej: 0.15 para 15%)
    annual_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        verbose_name="Tasa Anual"
    ) 
    
    clabe = models.CharField(max_length=18, unique=True, verbose_name="CLABE Interbancaria")
    
    card_number = models.CharField(
        max_length=16, 
        blank=True, 
        null=True,
        verbose_name="Número de Tarjeta"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        verbose_name = "Cuenta de Ahorro"
        verbose_name_plural = "Cuentas de Ahorro"
        ordering = ['name']