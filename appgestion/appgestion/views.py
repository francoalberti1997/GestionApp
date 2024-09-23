from django.shortcuts import get_object_or_404
from mp.models import Business, Subcategory, Category, Service
from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook_twilio(request):
    if request.method == 'POST':
        user_number = request.POST['From']  # Número del usuario
        user_input = request.POST['Body'].strip()  # Respuesta del usuario

        response = MessagingResponse()
