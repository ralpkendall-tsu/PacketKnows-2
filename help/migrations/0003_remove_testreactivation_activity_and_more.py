# Generated by Django 4.2.7 on 2024-01-07 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0002_alter_activity_options_and_more'),
        ('help', '0002_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testreactivation',
            name='activity',
        ),
        migrations.AddField(
            model_name='testreactivation',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='activity.activity'),
        ),
    ]
