from celery import shared_task
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from .models import Appointment


@shared_task
def appointment_created(appointment_id, username, recipient_list):
    appointment = get_object_or_404(Appointment, 
                                    id=appointment_id)
    subject = 'Appointment Confirmation'
    message = f'Dear {username},\n\nYou have successfully booked an\
        appointment with\ {appointment.doctor.user.username} on {appointment.date}.'
    mail_sent = send_mail(subject, message,
                          'admin@healthcare.com',
                          recipient_list)
    return mail_sent
