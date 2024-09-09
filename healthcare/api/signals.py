from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import CustomUser, Doctor, Patient


@receiver(signal=post_save, sender=CustomUser)
def create_user(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'doctor':
            Doctor.objects.create(user=instance)
        if instance.role == 'patient':
            Patient.objects.create(user=instance)


@receiver(signal=post_save, sender=CustomUser)
def save_user(sender, instance, **kwargs):
    if instance.role == 'doctor' and hasattr(instance, 'doctor'):
        instance.doctor.save()
    if instance.role == 'patient' and hasattr(instance, 'patient'):
        instance.patient.save()
    