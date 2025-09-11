from rest_framework import serializers
from rest_framework import serializers

class GoogleMeetEventSerializer(serializers.Serializer):
    summary = serializers.CharField()
    description = serializers.CharField()
    # attendees = serializers.ListField(
    #     child=serializers.DictField(child=serializers.EmailField()),
    #     required=True
    # )
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
