import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from expenses.models import Expense
from utils.create_installments_for import create_installments_for


def run():
    print("🔵 Generando mensualidades para gastos MSI sin installments...")

    # Obtiene todos los MSI que NO tienen installments
    expenses = Expense.objects.filter(is_msi=True, installments__isnull=True)

    total = 0
    for exp in expenses:
        create_installments_for(exp)
        total += 1

    print(f"✅ Listo: Se generaron mensualidades para {total} gastos MSI.")


if __name__ == "__main__":
    run()
