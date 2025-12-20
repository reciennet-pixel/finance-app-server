from datetime import timedelta
from django.utils import timezone
from expenses.models import Installment
from utils.payments import add_months

def create_installments_for(expense):
    """
    Crea la lista de pagos mensuales (installments) para un gasto a MSI.
    """
    if not expense.is_msi:
        return  # no aplica

    # Si ya existen installments, no duplicar
    if expense.installments.exists():
        return

    total_months = expense.months
    monthly_amount = expense.monthly_amount

    # Validar datos
    if not total_months or not monthly_amount:
        raise ValueError("El gasto MSI no tiene configurados meses o monthly_amount.")

    # Fecha base = fecha de creación del gasto
    start_date = expense.created_at.date()

    installments = []

    for i in range(total_months):
        due_date = add_months(start_date, i)

        inst = Installment(
            expense=expense,
            month_number=i + 1,
            amount=monthly_amount,
            due_date=due_date,
            is_paid=False
        )
        installments.append(inst)

    Installment.objects.bulk_create(installments)
    print(f"✔ Installments creados para {expense.title}")
