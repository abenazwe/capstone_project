from rest_framework import serializers
from .models import CustomUser, Meter, SensorData

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'name', 'password', ]
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['role'] = "Customer"
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UpdateCustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']

class UpdateAdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'role']

class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = ['product_id', 'name', 'location']

class SensorDataSerializer(serializers.ModelSerializer):
   # sensor_data_id = serializers.PrimaryKeyRelatedField(queryset=Meter.objects.all())

    class Meta:
        model = SensorData
        fields = '__all__'
        
        