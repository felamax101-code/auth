from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    service=serializers.CharField(required=True)
    wash_level=serializers.CharField(required=True)
    wash_type=serializers.CharField(required=True)
    car_type=serializers.CharField(required=True)
    booking_time=serializers.DateTimeField(required=True)
    arrival_time=serializers.DateTimeField(required=False)
    pickup=serializers.BooleanField(required=False)
    class Meta:
        model=Book
        fields=["service","wash_level","wash_type","car_type","booking_time","arrival_time","pickup"]
        
    # def validate(self,data):
    #     required=["service","wash_level","wash_type","car_type","booking_time","arrival_time","pickup"]
        # for obj in required:
        #     if obj not in data[""]:
        #         raise serializers.ValidationError(f"{obj} is required")
    def create(self,validated_data):
        book=Book.objects.create(**validated_data)
        return book
           