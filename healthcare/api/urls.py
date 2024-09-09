from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView, 
                                            TokenRefreshView, 
                                            TokenVerifyView)

from . import views


app_name = 'api'
router = DefaultRouter()
router.register(r'appointments', views.PatientAppointmentsViewSet, 
                basename='appointments')

urlpatterns = [
     path('register', views.RegisterView.as_view(),
          name='register'),
     path('doctors/', views.DoctorListView.as_view(),
         name='doctor_list'),
     path('doctors/schedule/', views.AddTimeSlotView.as_view(),
         name='add_availability'),
     path('doctors/appointments/', views.DoctorAppointmentsView.as_view(),
         name='doctor/appointments'),
     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
     path('', include(router.urls)),
]
