from datetime import date, timedelta
import calendar
from django.db.models import Sum

def add_months(d: date, months: int) -> date:
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return date(y, m, day)

def expense_paid_amount(expense):
    return expense.installments.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
