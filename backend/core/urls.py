from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views, auth_views

router = DefaultRouter()
router.register('doctors', views.DoctorViewSet, basename='doctor')
router.register('patients', views.PatientViewSet, basename='patient')
router.register('medicines', views.MedicineViewSet, basename='medicine')
router.register('templates', views.PrescriptionTemplateViewSet, basename='template')
router.register('prescriptions', views.PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats),

    # --- Auth ---
    path('auth/register/', auth_views.register_doctor),
    path('auth/login/', auth_views.LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/me/', auth_views.me),

    # --- Assistant management (doctor-only) ---
    path('assistants/', auth_views.assistants),
    path('assistants/<int:pk>/', auth_views.assistant_detail),
    path('assistants/<int:pk>/reset-password/', auth_views.reset_assistant_password),
]
