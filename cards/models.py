from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.CharField(max_length=50)
    card_type = models.CharField(max_length=20)  # crédito/debito
    last_digits = models.CharField(max_length=4)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    cut_off_date = models.IntegerField(null=True)
    payment_due_date = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to='card_icons/', blank=True, null=True)
    def __str__(self):
        return f"{self.bank} ****{self.last_digits}"