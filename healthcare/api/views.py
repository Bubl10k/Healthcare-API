from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, 
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, 
                                   HTTP_404_NOT_FOUND)
from rest_framework.views import APIView

from api.models import Appointment, CustomUser, Doctor
from api.serializers import (AppointmentSerializer, 
                             DoctorSerializer, RegisterSerializer,
                             TimeSlotSerializer)
from api.permissions import DoctorPermission, PatientPermission
from api.tasks import appointment_created

# Create your views here. 
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    

class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, DoctorPermission]


class AddTimeSlotView(APIView):
    """
    Adds availability
    """
    permission_classes = [IsAuthenticated, DoctorPermission]
    
    def post(self, request, format=None):
        serializer = TimeSlotSerializer(data=request.data,
                                        context={'request': request})
        doctor = request.user.doctor
        
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class DoctorAppointmentsView(APIView):
    permission_classes = [IsAuthenticated, DoctorPermission]
    
    def get(self, request, format=None):
        queryset = Appointment.objects.\
            filter(doctor=request.user.doctor)
        serializer = AppointmentSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class PatientAppointmentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, PatientPermission]
    
    def list(self, request):
        queryset = Appointment.objects.all()
        serializer = AppointmentSerializer(queryset, many=True)
        return Response(data=serializer.data)
    
    def create(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save(patient=request.user.patient)
            recipient_list = [request.user.email]
            appointment_created.delay(appointment.id, request.user.username,
                                recipient_list)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            appointment = get_object_or_404(Appointment, pk=pk)
            appointment.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        except Appointment.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
    
    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated,
                                PatientPermission])
    def patient_appointments(self, request):
        queryset = request.user.patient.appointments.all()
        serializer = AppointmentSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(methods=['patch'],
            detail=True,
            permission_classes=[IsAuthenticated,
                                PatientPermission])
    def reschedule(self, request, pk=None):
        appointment = get_object_or_404(Appointment,
                                        pk=pk,
                                        patient=request.user.patient)
        new_date = request.data.get('date')
        appointment.date = new_date
        serializer = AppointmentSerializer(appointment,
                                           data=request.data,
                                           partial=True)
        appointment_created.delay(appointment.id, request.user.username,
                                [request.user.email])
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({'detail': 'This doctor already has an appointment at the new time.'}, 
                        status=HTTP_400_BAD_REQUEST)
        