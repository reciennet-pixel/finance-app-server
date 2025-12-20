# cards/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet

router = DefaultRouter()
router.register(r'cards', CardViewSet, basename='card')

urlpatterns = [
    path('', include(router.urls)),
    # path(
    #     'cards/<int:card_id>/expenses/<int:pk>/toggle/',
    #     ExpenseViewSet.as_view({'patch': 'toggle_paid'})
    #     ),
    # path('cards/<int:card_id>/expenses/', ExpenseViewSet.as_view({"get": "list", "post": "create"})),
    # path(
    #     'cards/<int:card_id>/expenses/<int:pk>/',
    #     ExpenseViewSet.as_view({
    #         "get": "retrieve",
    #         "put": "update",
    #         "patch": "partial_update",
    #         "delete": "destroy"
    #     })
    # ),
    # path('cards/<int:card_id>/pay/', ExpenseViewSet.as_view({"post": "pay_month"})),
    # path(
    #     'cards/<int:card_id>/expenses/<int:pk>/toggle/',
    #     ExpenseViewSet.as_view({'patch': 'toggle_paid'})
    # )
]
