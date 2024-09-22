from django.shortcuts import get_object_or_404
from mp.models import Business, Subcategory, Category, Service
from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Diccionario para almacenar el estado de cada usuario
user_states = {}

def start_conversation(response):
    response.message(
        "Hola, ¿qué deseas hacer hoy?\n"
        "1️⃣ Ver categorías\n"
        "2️⃣ Consultar estado de mi pedido\n"
        "3️⃣ Contactar atención al cliente"
    )
    return 'asking_initial_options'

def show_categories(response):
    categories = Category.objects.all()
    category_message = "Selecciona una categoría:\n"
    for idx, category in enumerate(categories, start=1):
        category_message += f"{idx}️⃣ {category.name}\n"
    response.message(category_message)
    return 'asking_category'

def show_subcategories(response, category):
    subcategories = Subcategory.objects.filter(category=category)
    subcategory_message = f"Seleccionaste *{category.name}*. ¿Qué subcategoría te interesa?\n"
    for idx, subcategory in enumerate(subcategories, start=1):
        subcategory_message += f"{idx}️⃣ *{subcategory.name}*\n"
    response.message(subcategory_message)
    return 'asking_subcategory'

def show_businesses(response, subcategory):
    businesses = Business.objects.filter(subcategory=subcategory)
    business_message = f"Negocios en la subcategoría *{subcategory.name}*:\n"
    for idx, business in enumerate(businesses, start=1):
        business_message += f"{idx}️⃣ {business.name}\n"
    response.message(business_message)
    return 'asking_business'

def show_services(response, business):
    services = business.services.all()  # Acceder a los servicios del negocio
    service_message = f"Servicios disponibles en *{business.name}*:\n"
    for idx, service in enumerate(services, start=1):
        service_message += f"{idx}️⃣ {service.name}: ${service.price}\n"
    response.message(service_message)
    return 'done'

@csrf_exempt
def webhook_twilio(request):
    if request.method == 'POST':
        user_number = request.POST['From']  # Número del usuario
        user_input = request.POST['Body'].strip()  # Respuesta del usuario

        response = MessagingResponse()

        # Verificar el estado actual del usuario en la conversación
        if user_number not in user_states:
            user_states[user_number] = start_conversation(response)
        
        elif user_states[user_number] == 'asking_initial_options':
            if user_input == '1':
                user_states[user_number] = show_categories(response)
            elif user_input == '2':
                response.message("Consultando el estado de tu pedido...")
                user_states[user_number] = 'done'
            elif user_input == '3':
                response.message("Te estoy conectando con atención al cliente.")
                user_states[user_number] = 'done'
            else:
                response.message("Por favor, selecciona una opción válida.")
        
        elif user_states[user_number] == 'asking_category':
            try:
                category_index = int(user_input) - 1
                categories = Category.objects.all()
                selected_category = categories[category_index]
                user_states[user_number] = show_subcategories(response, selected_category)
                user_states[f'{user_number}_category_id'] = selected_category.id  # Guardar el ID de la categoría
            except (ValueError, IndexError):
                response.message("Por favor, selecciona una categoría válida.")
        
        elif user_states[user_number] == 'asking_subcategory':
            try:
                subcategory_index = int(user_input) - 1
                category_id = user_states.get(f'{user_number}_category_id')  # Obtener el ID de la categoría
                if category_id:
                    category = Category.objects.get(id=category_id)
                    selected_subcategory = Subcategory.objects.filter(category=category)[subcategory_index]
                    user_states[user_number] = show_businesses(response, selected_subcategory)
                    user_states[f'{user_number}_subcategory_id'] = selected_subcategory.id  # Guardar el ID de la subcategoría
                else:
                    response.message("No se ha seleccionado ninguna categoría.")
            except (ValueError, IndexError, Category.DoesNotExist):
                response.message("Por favor, selecciona una subcategoría válida.")
        
        elif user_states[user_number] == 'asking_business':
            try:
                business_index = int(user_input) - 1
                subcategory_id = user_states.get(f'{user_number}_subcategory_id')  # Obtener el ID de la subcategoría
                if subcategory_id:
                    selected_subcategory = Subcategory.objects.get(id=subcategory_id)
                    selected_business = Business.objects.filter(subcategory=selected_subcategory)[business_index]
                    user_states[user_number] = show_services(response, selected_business)
                else:
                    response.message("No se ha seleccionado ninguna subcategoría.")
            except (ValueError, IndexError, Subcategory.DoesNotExist):
                response.message("Por favor, selecciona un negocio válido.")

        return HttpResponse(str(response), content_type='application/xml')
