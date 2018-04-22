from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from athanor.rest.serial import WhoAccountSerializer, WhoCharacterSerializer, WhoAccount, WhoCharacter


class WhoAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WhoAccount.objects.order_by('account__db_key')
    serializer_class = WhoAccountSerializer


class WhoCharacterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WhoCharacter.objects.order_by('character__db_key')
    serializer_class = WhoCharacterSerializer
    
def router():
    r = DefaultRouter()
    r.register(r'who_account', WhoAccountViewSet)
    r.register(r'who_character', WhoCharacterViewSet)
    return r