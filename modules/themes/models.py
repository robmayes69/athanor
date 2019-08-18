from django.db import models


class StatusText(models.Model):
    key = models.CharField(blank=False, null=False, unique=True)


class TypeText(models.Model):
    key = models.CharField(blank=False, null=False, unique=True)


class CharacterStatus(models.Model):
    character_stub = models.OneToOneField('core.ObjectStub', related_name='theme_status', on_delete=models.CASCADE)
    status = models.ForeignKey(StatusText, related_name='character_status', null=True, on_delete=models.SET_NULL)


class Theme(models.Model):
    key = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)


class ThemeParticipant(models.Model):
    theme = models.ForeignKey(Theme, related_name='participants', on_delete=models.CASCADE)
    character_status = models.ForeignKey(CharacterStatus, related_name='participating_in', on_delete=models.CASCADE)
    list_type = models.ForeignKey(TypeText, related_name='used_by', on_delete=models.DO_NOTHING)
