from rest_framework import serializers
from .models import  DoctorLanguages

class DoctorLanguagesSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source='language.language', read_only=True)
    class Meta:
        model = DoctorLanguages
        fields = ['language']

