from rest_framework import serializers
from athanor.models import WhoAccount, WhoCharacter

class WhoAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhoAccount
        fields = ('account', 'is_dark', 'is_hidden')
        
        
class WhoCharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhoCharacter
        fields = ('character', 'is_dark', 'is_hidden')