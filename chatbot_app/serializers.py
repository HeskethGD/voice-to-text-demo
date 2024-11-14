from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()

class ChatbotInputSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)