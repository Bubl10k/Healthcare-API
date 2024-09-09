from django.contrib import admin

from .models import Appointment, CustomUser, Doctor, Patient, TimeSlot

# Register your models here.
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth']
    list_filter = ['user', 'date_of_birth']
    date_hierarchy = 'date_of_birth'
    

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'years_of_experience']
    list_filter = ['user', 'specialization', 'years_of_experience']
    

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date']
    list_filter = ['patient', 'doctor', 'date']
    date_hierarchy = 'date'


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time']
    list_filter = ['doctor']
    date_hierarchy = 'date'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['role', 'username']
    