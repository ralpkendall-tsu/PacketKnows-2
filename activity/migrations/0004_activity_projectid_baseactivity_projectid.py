# Generated by Django 4.2.7 on 2024-01-09 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0003_baseactivity_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='projectID',
            field=models.CharField(default='ewewe213', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='baseactivity',
            name='projectID',
            field=models.CharField(default='ewefwfw', max_length=255),
            preserve_default=False,
        ),
    ]
