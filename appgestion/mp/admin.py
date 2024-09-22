from django.contrib import admin
from .models import Business, Category, Subcategory, Service, Appointment, Customer

admin.site.register(Business)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Customer)