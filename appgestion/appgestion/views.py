from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from redis import Redis
from mp.models import Category, Subcategory, Business, Service

# Configura la conexión a Redis
redis_client = Redis(host='localhost', port=6379, db=0)

def listar_opciones(queryset, attribute_name, price_attribute=None):
    options = []
    for i, item in enumerate(queryset):
        option_str = f"{i + 1} - {getattr(item, attribute_name)}"
        if price_attribute:
            option_str += f" Precio: ${int(getattr(item, price_attribute))} \n"
        options.append(option_str)
    return "\n".join(options)

@csrf_exempt
def webhook_twilio(request):
    if request.method == 'POST':
        user_number = request.POST.get('From')  # Número del usuario
        user_input = request.POST.get('Body').strip()  # Respuesta del usuario

        # Obtén todos los valores del hash desde Redis
        values = redis_client.hgetall(user_number)

        # Decodifica los valores de bytes a strings
        state = values.get(b'state').decode('utf-8') if values.get(b'state') else None
        category_obj = int(values.get(b'category').decode('utf-8')) if values.get(b'category') else None
        sub_category_obj = int(values.get(b'subcategory').decode('utf-8')) if values.get(b'subcategory') else None
        business_obj = int(values.get(b'business').decode('utf-8')) if values.get(b'business') else None
        service_obj = str(values.get(b'service').decode('utf-8')) if values.get(b'service') else None

        # Crea la respuesta de Twilio
        response = MessagingResponse()

        # Si no hay estado, lo inicializamos a "Greeting"
        if state is None:
            redis_client.hset(user_number, "state", "Category")
            response.message("""Hola! Bienvenido a Gestapp. Por favor, selecciona una de las siguientes opciones: 
            1 - Para ver Categorías 
            """)

        elif state == "Category":
            if user_input != "1":
                response.message("Opción inválida. \n 1 - Para ver Categorías ")
            else:
                redis_client.hset(user_number, "state", "Subcategory")
                categories = Category.objects.all()
                message = listar_opciones(categories, "name")
                response.message(message)

        elif state == "Subcategory":
            try: 
                user_input = int(user_input)
                user_input = user_input - 1 
                redis_client.hset(user_number, "category", user_input)

                category_obj = Category.objects.all()[user_input]

                sub_categories = Subcategory.objects.filter(category=category_obj)
                message = listar_opciones(sub_categories, "name")
                response.message(message)
                redis_client.hset(user_number, "state", "Businesses")

            except ValueError:
                response.message("No válido. Sólo nros.")

        elif state == "Businesses":
            try: 
                user_input = int(user_input)
                user_input = user_input - 1

                category_obj = Category.objects.all()[category_obj]
                subcategory = Subcategory.objects.filter(category=category_obj)[user_input]

                redis_client.hset(user_number, "subcategory", user_input)

                businesses = Business.objects.filter(subcategory=subcategory)

                message = listar_opciones(businesses, "name")
                response.message(message)
                redis_client.hset(user_number, "state", "Services")

            except ValueError:
                response.message("No válido. Sólo nros.")                            
        
        elif state == "Services":
            try: 
                user_input = int(user_input)
                user_input = user_input - 1

                category_obj = Category.objects.all()[category_obj]
                subcategory = Subcategory.objects.filter(category=category_obj)[sub_category_obj]
                business = Business.objects.filter(subcategory=subcategory)[user_input]

                redis_client.hset(user_number, "business", user_input)

                services = Service.objects.filter(business=business)

                message = listar_opciones(services, "name", "price")
                response.message(message)
                redis_client.hset(user_number, "state", "MP")

            except ValueError:
                response.message("No válido. Sólo nros.")

        elif state == "MP":
            user_input = int(user_input)
            user_input = user_input - 1

            category_obj = Category.objects.all()[category_obj]
            subcategory = Subcategory.objects.filter(category=category_obj)[sub_category_obj]
            business = Business.objects.filter(subcategory=subcategory)[business_obj]
            service = Service.objects.filter(business=business)[user_input]
            service_token = service.token

            redis_client.hset(user_number, "service", service_token)

            response.message(f"http://127.0.0.1:8000/mp/check/{service_token}/")

        return HttpResponse(str(response), content_type='application/xml')


