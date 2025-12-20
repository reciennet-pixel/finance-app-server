from django.shortcuts import render
# cards/views.py
from datetime import date, timedelta
from django.db import transaction
from rest_framework import viewsets

from cards.models import Card
from earnings.models import SavingsAccount
from .models import Expense, Installment
from .serializers import  ExpenseSerializer, InstallmentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Q

# Create your views here.
class ExpenseViewSet(viewsets.ModelViewSet):
    
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        card_id = self.kwargs.get("card_id")
        qs = Expense.objects.filter(card_id=card_id)

        status = self.request.query_params.get("status")

        if status == "paid":
            qs = qs.filter(is_paid=True)
        elif status == "unpaid":
            qs = qs.filter(is_paid=False)

        return qs.order_by("-created_at")
    
    def perform_create(self, serializer):
        # Overridden so create() can call a helper to build installments if needed
        expense = serializer.save()
        if expense.is_msi and expense.months and expense.monthly_amount:
            self._create_installments(expense)

    #  @transaction.atomic
    def _create_installments(self, expense):
        """
        Crea `months` Installment para el expense.
        La due_date se puede calcular tomando created_at y agregando meses.
        """
        # helper to add months safely:
        def add_months(d, months):
            import calendar
            m = d.month - 1 + months
            y = d.year + m // 12
            m = m % 12 + 1
            day = min(d.day, calendar.monthrange(y, m)[1])
            return date(y, m, day)

        base_date = expense.created_at.date() if expense.created_at else date.today()
        installments = []
        amount_each = expense.monthly_amount or (expense.amount / expense.months)
        for i in range(1, int(expense.months) + 1):
            due = add_months(base_date, i)  # primer pago al mes siguiente
            inst = Installment(
                expense=expense,
                month_number=i,
                amount=amount_each,
                due_date=due
            )
            installments.append(inst)
        Installment.objects.bulk_create(installments)
    def pay_month(self, request, card_id=None):
        """
        Acción a nivel tarjeta: marca las cuotas correspondientes al mes actual como pagadas.
        Lógica: todas las installments cuyo due_date esté dentro del mes actual.
        """
        today = date.today()
        first_day = today.replace(day=1)
        last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - timedelta(days=1))
        installments = Installment.objects.filter(
            expense__card_id=card_id,
            is_paid=False,
            due_date__gte=first_day,
            due_date__lte=last_day
        )
        with transaction.atomic():
            for inst in installments:
                inst.is_paid = True
                inst.save()
                # each expense check
                exp = inst.expense
                paid_count = exp.installments.filter(is_paid=True).count()
                if paid_count >= (exp.months or 0):
                    exp.is_paid = True
                    exp.paid_month = first_day
                exp.remaining_months = max(0, (exp.months or 0) - paid_count)
                exp.save()
        return Response({'message':'Pago del mes aplicado', 'count': installments.count()})
    def toggle_paid(self, request, card_id=None, pk=None):
        # toggle is_paid for the expense (liquidar o desmarcar)
        expense = self.get_object()
        expense.is_paid = not expense.is_paid
        if expense.is_paid:
            expense.paid_month = date.today().replace(day=1)
        else:
            expense.paid_month = None
        expense.save()
        return Response({'is_paid': expense.is_paid})
    
    def set_paid_months(self, request, card_id=None, pk=None):
        """
        Body: { "paid_months": 5 } -> marca las primeras 5 cuotas como pagadas.
        """
        expense = self.get_object()
        paid_months = int(request.data.get('paid_months', 0))
        if not expense.is_msi:
            return Response({'detail':'Expense is not MSI'}, status=400)

        installments = list(expense.installments.order_by('month_number'))
        with transaction.atomic():
            for inst in installments:
                inst.is_paid = inst.month_number <= paid_months
                inst.save()
            # update remaining_months field (optional)
            expense.remaining_months = max(0, expense.months - paid_months)
            # if all paid, mark expense.is_paid
            if paid_months >= expense.months:
                expense.is_paid = True
                expense.paid_month = date.today().replace(day=1)
            else:
                expense.is_paid = False
                expense.paid_month = None
            expense.save()

        return Response({'paid_months': paid_months})

    def pay_installment(self, request, card_id=None, pk=None, inst_pk=None):
        """
        Marca una cuota individual como pagada o no pagada.
        PATCH body optional: { "is_paid": true }
        """
        try:
            inst = Installment.objects.get(pk=inst_pk, expense_id=pk)
        except Installment.DoesNotExist:
            return Response({'detail':'Installment not found'}, status=404)

        is_paid = request.data.get('is_paid')
        if is_paid is None:
            # toggle
            inst.is_paid = not inst.is_paid
        else:
            inst.is_paid = bool(is_paid)
        inst.save()

        # actualizar expense.remaining_months (opcional) y estado
        expense = inst.expense
        paid_count = expense.installments.filter(is_paid=True).count()
        expense.remaining_months = expense.months - paid_count if expense.months else None
        if paid_count >= (expense.months or 0):
            expense.is_paid = True
            expense.paid_month = date.today().replace(day=1)
        else:
            expense.is_paid = False
            expense.paid_month = None
        expense.save()

        return Response(InstallmentSerializer(inst).data)
    
    def get_graphics(self, request):
        user = request.user
        
        # 1. Lógica para Gráfica 1: Deuda por Tarjeta
        cards = Card.objects.filter(user=user)
        cards_data = []
        total_debt_global = 0

        for card in cards:
            # Sumamos solo las mensualidades que NO están pagadas de esta tarjeta
            # 1. Sumamos gastos normales (NO MSI) que no están pagados
            normal_expenses = Expense.objects.filter(
                card=card, 
                is_msi=False, 
                is_paid=False
            ).aggregate(total=Sum('amount'))['total'] or 0

            # 2. Sumamos mensualidades de MSI que no están pagadas
            msi_debt = Installment.objects.filter(
                expense__card=card,
                is_paid=False
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # La deuda real es la suma de ambos
            unpaid_debt = normal_expenses + msi_debt
            
            total_debt_global += unpaid_debt
            
            cards_data.append({
                "label": f"{card.bank} ({card.last_digits})",
                "amount": float(unpaid_debt)
            })

        # 2. Lógica para Gráfica 2: Deuda vs Ganancias (Ahorros)
        total_savings = SavingsAccount.objects.filter(user=user).aggregate(
            total=Sum('initial_amount')
        )['total'] or 0

        return Response({
            "by_card": cards_data,
            "global_comparison": {
                "debt": float(total_debt_global),
                "savings": float(total_savings)
            }
        })
    
    
    def get_financial_summary(self, request):
        user = request.user # O el ID que estés usando por ahora
        
        # 1. GANANCIAS TOTALES (Ahorros / Inversiones)
        # Asegúrate de que SavingsAccount sí tenga el campo 'user'
        total_savings = SavingsAccount.objects.filter(user=user).aggregate(
            total=Sum('initial_amount')
        )['total'] or 0

        # 2. CALCULO DE DEUDA DINÁMICA
        # Filtramos Expenses a través de la relación con la tarjeta del usuario
        credit_expenses = Expense.objects.filter(
            card__user=user,              # <--- Corrección: Buscamos el usuario en la tarjeta
            card__card_type__iexact='crédito'
        )

        # A. Gastos a una exhibición (is_msi=False)
        single_payment_debt = credit_expenses.filter(
            is_msi=False
        ).aggregate(total=Sum('amount'))['total'] or 0

        # B. Gastos a meses (Saldo pendiente real)
        # Sumamos el 'monthly_amount' multiplicado por 'remaining_months' 
        # para saber cuánto debemos realmente a futuro.
        # Si prefieres solo el total del gasto, usa Sum('amount')
        installment_debt = credit_expenses.filter(
            is_msi=True
        ).aggregate(total=Sum('amount'))['total'] or 0  

        total_debt = float(single_payment_debt) + float(installment_debt)

        # 3. LÍMITE TOTAL DE CRÉDITO
        total_limit = Card.objects.filter(
            user=user, 
            card_type__iexact='crédito'
        ).aggregate(total=Sum('credit_limit'))['total'] or 1

        # 4. PORCENTAJE DE USO
        usage_percentage = (total_debt / float(total_limit)) * 100

        data = {
            "user_name": user.first_name if user.first_name else user.username,
            "total_balance": float(total_savings),
            "credit_card_debt": total_debt,
            "credit_limit_total": float(total_limit),
            "usage_percentage": round(usage_percentage, 1),
            "is_healthy": float(total_savings) > total_debt 
        }
        return Response(data)