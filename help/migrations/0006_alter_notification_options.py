# Generated by Django 4.2.7 on 2024-01-14 02:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0005_testreactivation_classroom_testreactivation_student'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at'], 'verbose_name_plural': 'Notifications'},
        ),
    ]
