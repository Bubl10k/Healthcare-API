from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from rest_framework.validators import UniqueValidator

from api.models import Appointment, CustomUser, Doctor, Patient, TimeSlot


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, 
                                     required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, 
                                     required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2', 
                  'email', 'first_name', 'last_name', 'role')
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError('Password fields don\'t match')
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            role=validated_data.get('role')   
        )
        
        user.set_password(validated_data.get('password'))
        user.save()

        return user
        

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        

class TimeSlotSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = '__all__'
    
    def validate(self, attrs):
        doctor = self.context['request'].user.doctor
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        date = attrs.get('date')
        time_slot = TimeSlot.objects.filter(doctor=doctor,
                                            date=date,
                                            start_time__lte=end_time,
                                            end_time__gte=start_time)\
                                                .exists()
        if time_slot:
            raise serializers.ValidationError('This doctor already has an overlapping time slot.')
        return attrs
        

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient = StringRelatedField(read_only=True)
    doctor = StringRelatedField(read_only=True)
    
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), write_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, attrs):
        '''
        Custom validation to check for overlapping appointments for the doctor.
        '''
        doctor = attrs.get('doctor_id')
        date = attrs.get('date')
        appointment = Appointment.objects.filter(doctor=doctor,
                                                 date=date).exists()
        if appointment:
            raise serializers.ValidationError('This doctor already has an appointment at the same time.')
        return attrs
    
    def create(self, validated_data):
        doctor = validated_data.pop('doctor_id')
        return Appointment.objects.create(doctor=doctor, **validated_data)
    