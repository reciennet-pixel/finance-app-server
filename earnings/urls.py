from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SavingsAccountViewSet

# Crea un router y registra nuestro ViewSet
router = DefaultRouter()
router.register(r'accounts', SavingsAccountViewSet, basename='savingsaccount')

# Las URL generadas serán:
# /earnings/accounts/       (GET: Listar, POST: Crear)
# /earnings/accounts/{id}/  (GET: Detalle, PUT/PATCH: Actualizar, DELETE: Borrar)

urlpatterns = [
    path('', include(router.urls)),
]