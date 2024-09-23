from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import mercadopago
from twilio.twiml.messaging_response import Message, MessagingResponse
from .models import Business

@csrf_exempt
def home(request):
    return render(request, "home.html")

@csrf_exempt
def check_pro_render(request, name=None):
    if name:

        business = Business.objects.filter(name=name).first()
        sdk = mercadopago.SDK(business.access_token)        

        preference_data = {
            "items": [
                {
                    "title": f"Producto de {business.name}",
                    "quantity": 1,
                    "unit_price": 1250
                }
            ]
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        preference_id = preference["id"]

        context = {
            "preference_id":preference_id,
            "public_key": business.public_key
        }

        return render(request, "pro-check.html", context)

    
