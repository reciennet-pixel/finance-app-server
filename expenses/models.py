from django.db import models

from cards.models import Card
# Create your models here.
class Expense(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    is_msi = models.BooleanField(default=False)
    months = models.IntegerField(null=True, blank=True)  # 3, 6, 12, 24...
    monthly_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)  # si ya se pagó
    paid_month = models.DateField(null=True, blank=True)  # mes en que se liquidó

    remaining_months = models.IntegerField(null=True, blank=True)  # para MSI   

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Installment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="installments")
    month_number = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago {self.month_number} de {self.expense.title}"
