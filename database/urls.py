from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'staff', views.StaffAPIViewSet)
router.register(r'contributions', views.ContributionViewSet)
router.register(r'memberships', views.MembershipViewSet)
router.register(r'schemes', views.InvestmentSchemeViewSet)
router.register(r'tenants', views.TenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]