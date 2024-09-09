from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from django.utils import timezone

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    role = models.CharField(max_length=10,
                            choices=ROLE_CHOICES)
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username
    

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser,
                                on_delete=models.CASCADE,
                                related_name='doctor')
    specialization = models.CharField(max_length=100,
                                      blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    objects = models.Manager()
    
    def __str__(self):
        return f'Doctor {self.user.username} - {self.specialization}'


class Patient(models.Model):
    user = models.OneToOneField(CustomUser, 
                                on_delete=models.CASCADE,
                                related_name='patient')
    date_of_birth = models.DateField(blank=True,
                                     null=True)
    medical_history = models.TextField(blank=True,
                                       null=True)
    objects = models.Manager()
    
    def __str__(self):
        return f'Patient {self.user.username}'
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    patient = models.ForeignKey(Patient, 
                                   on_delete=models.CASCADE,
                                   related_name='appointments')
    doctor = models.ForeignKey(Doctor, 
                                  on_delete=models.CASCADE,
                                  related_name='appointments')
    date = models.DateTimeField()
    status = models.CharField(max_length=100,
                              choices=STATUS_CHOICES,
                              default='booked')
    objects = models.Manager()
    
    def __str__(self):
        return f'Appointment {self.patient.user.username} - {self.doctor.user.username} - {self.date}'
    

class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, 
                               on_delete=models.CASCADE, 
                               related_name='available_time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    objects = models.Manager()
    
    def __str__(self):
        return f'{self.doctor.user.username} - {self.date} - {self.start_time} - {self.end_time}'
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time.")
        if self.date < timezone.now().date():
            raise ValidationError("Time slot cannot be in the past.")
