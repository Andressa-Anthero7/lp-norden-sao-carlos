from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Leads(models.Model):
    nome_leads = models.CharField(max_length=50)
    whats_app_leads = models.CharField(max_length=12)
    data_recebimento = models.CharField(max_length=8)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        combined_string = f"{self.pk}/{self.nome_leads}/{self.whats_app_leads}/{self.data_recebimento}/"
        return combined_string

    def get_absolute_url(self):
        return reverse("landingpage", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            combined_string = f"{self.pk}-{self.nome_leads}-{self.whats_app_leads}-{self.data_recebimento}"
            self.slug = slugify(combined_string)
        return super().save(*args, **kwargs)


class Config_WhatsApp(models.Model):
    numero_whats_app = models.CharField(max_length=11, blank=False, null=False, default='Somente números e sem espaço')
    chave_api_whats_app = models.CharField(max_length=50)

    def __str__(self):
        return self.numero_whats_app
        