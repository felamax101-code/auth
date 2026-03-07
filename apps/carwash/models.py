from django.db import models

class Book(models.Model):
    service=models.CharField(choices={
        "car wash":" Car Wash",
        "garage service":"Garage Service"
    })
    wash_level=models.CharField(choices={
        "basic wash":"Basic Wash",
        "premium wash":"Premium Wash"
    })
    wash_type=models.CharField(choices={
        "interior":"Interior",
        "exterior":"Exterior",
        "interior & exterior":"Interior & Exterior"
    })
    car_type=models.CharField(choices={
        "truck":"Truck",
        "vehicle":"Vehicle",
        "motorcycle":"Motorcycle"
    })
    booking_time=models.DateTimeField(auto_now_add=True)
    arrival_time=models.DateTimeField()
    pickup=models.BooleanField(null=True,blank=True)
    
    
    def __str__(self):
        return (f"{self.service}|{self.car_type}|{self.wash_type}")