# Generated by Django 4.2.7 on 2024-01-07 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0002_alter_activity_options_and_more'),
        ('help', '0003_remove_testreactivation_activity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testreactivation',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.activity'),
        ),
    ]