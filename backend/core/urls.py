from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('doctors', views.DoctorViewSet)
router.register('patients', views.PatientViewSet)
router.register('medicines', views.MedicineViewSet)
router.register('templates', views.PrescriptionTemplateViewSet)
router.register('prescriptions', views.PrescriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats),
]
