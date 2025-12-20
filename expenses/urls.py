from django.urls import path
from .views import ExpenseViewSet
from rest_framework.routers import DefaultRouter


expense_list = ExpenseViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

expense_detail = ExpenseViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

pay_month = ExpenseViewSet.as_view({'post':'pay_month'})
set_paid_months = ExpenseViewSet.as_view({'post':'set_paid_months'})

urlpatterns = [
    path('cards/<int:card_id>/expenses/', expense_list, name='expense-list'),
    path('cards/<int:card_id>/expenses/<int:pk>/', expense_detail, name='expense-detail'),
    path('cards/<int:card_id>/pay/', pay_month, name='card-pay-month'),
    path('cards/<int:card_id>/expenses/<int:pk>/set-paid-months/', set_paid_months, name='set-paid-months'),
    path('cards/<int:card_id>/expenses/<int:pk>/installments/<int:inst_pk>/pay/', ExpenseViewSet.as_view({'patch':'pay_installment'}), name='pay-installment'),
    path('dashboard/summary/', ExpenseViewSet.as_view({'get':'get_graphics'}), name='finance-summary'),
    path('financial-summary/', ExpenseViewSet.as_view({'get':'get_financial_summary'}), name='financial-summary'),
]
