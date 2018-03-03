from django.db import models

from dwarf.models import Guild


class Wiki(models.Model):
    guild = models.OneToOneField(Guild, on_delete=models.CASCADE, primary_key=True)
    root = models.CharField(max_length=256)

    @property
    def api_url(self):
        return self.root + 'api.php'

    @property
    def article_url(self):
        return self.root + 'index.php?title='

    class Meta:
        app_label = 'dwarf'
