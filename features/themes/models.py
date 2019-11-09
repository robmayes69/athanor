from django.db import models


class ThemeStatus(models.Model):
    key = models.CharField(max_length=50, blank=False, null=False, unique=True)


class ThemeType(models.Model):
    key = models.CharField(max_length=50, blank=False, null=False, unique=True)


class ThemeCharacterStatus(models.Model):
    character_stub = models.OneToOneField('core.ObjectStub', related_name='theme_status', on_delete=models.CASCADE)
    status = models.ForeignKey(ThemeStatus, related_name='character_status', null=True, on_delete=models.SET_NULL)


class Theme(models.Model):
    key = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)


class ThemeParticipant(models.Model):
    theme = models.ForeignKey(Theme, related_name='participants', on_delete=models.CASCADE)
    character_status = models.ForeignKey(ThemeCharacterStatus, related_name='participating_in', on_delete=models.CASCADE)
    list_type = models.ForeignKey(ThemeType, related_name='used_by', on_delete=models.DO_NOTHING)
