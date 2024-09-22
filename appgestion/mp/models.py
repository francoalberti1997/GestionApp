from django.db import models
from django.contrib.auth.models import User  # Si usas el modelo de usuario de Django

class Category(models.Model):
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name

class Business(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    twilio_number = models.CharField(max_length=20, null=True, blank=True)
    public_key = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    mail = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    #direccion
    #horarios
    
    def __str__(self):
        return self.name

class Service(models.Model):  # Corregido el nombre del modelo
    name = models.CharField(max_length=100)
    price = models.FloatField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="services")  # Relación con Business

class Appointment(models.Model):
    PAYMENT_METHODS = [
        ("CASH","CASH"),
        ("TRANSFER","TRANSFER")
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)  
    date = models.DateField()  
    start_time = models.TimeField()  
    is_paid = models.BooleanField(default=False)  
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    class Meta:
        unique_together = ('business', 'service', 'date', 'start_time')  # Unicidad por negocio, servicio, fecha y hora

    def __str__(self):
        return f"{self.service.name} - {self.date} {self.start_time} ({'TRANSFER' if self.is_paid else 'CASH'})"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20) 
    mail = models.CharField(max_length=20) 
    date_birth = models.DateField()
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
