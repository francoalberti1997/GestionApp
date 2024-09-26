from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import mercadopago
from twilio.twiml.messaging_response import Message, MessagingResponse
from .models import Business, Service
from django.http import HttpResponse
from django.shortcuts import redirect

@csrf_exempt
def home(request):
    return render(request, "home.html")
@csrf_exempt
def check_pro_render(request, token=None):
    if token:        
        service = Service.objects.filter(token=token).first()

        if not service:
            return HttpResponse("Servicio no encontrado.", status=404)

        business = service.business
        
        # Verifica que el access_token sea un string válido
        access_token = business.access_token
        if not isinstance(access_token, str) or not access_token:
            return HttpResponse("Access token no válido.", status=400)

        # Inicializa el SDK
        sdk = mercadopago.SDK(access_token)

        preference_data = {
            "items": [
                {
                    "title": service.name,
                    "quantity": 1,
                    "unit_price": service.price
                }
            ]
        }

        # Crea la preferencia
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        preference_id = preference["id"]

        context = {
            "preference_id": preference_id,
            "public_key": business.public_key
        }

        checkout_url = preference["init_point"]

        # Redirige al usuario directamente al checkout de Mercado Pago
        return redirect(checkout_url)

def webhookMP(request):
    if request.method == 'POST':
        print("*")        
        print(request.POST)
        print("*")