# Generated by Django 4.2.7 on 2024-01-07 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'verbose_name_plural': 'Notifications'},
        ),
        migrations.AlterModelOptions(
            name='studentidchange',
            options={'verbose_name_plural': 'Student ID Changes'},
        ),
        migrations.AlterModelOptions(
            name='testreactivation',
            options={'verbose_name_plural': 'Test Reactivations'},
        ),
    ]
