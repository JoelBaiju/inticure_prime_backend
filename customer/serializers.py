# serializers.py
from rest_framework import serializers
from .models import CustomerProfile

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        read_only_fields = ['user']  # user will be set from the request
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)