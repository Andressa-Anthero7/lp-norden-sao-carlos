# Generated by Django 4.2.6 on 2024-12-27 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_leads_data_recebimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='leads',
            name='status_envelope',
            field=models.CharField(default='fechado', max_length=7),
        ),
    ]