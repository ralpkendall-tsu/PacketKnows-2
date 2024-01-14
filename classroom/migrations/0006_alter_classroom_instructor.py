# Generated by Django 4.2.7 on 2024-01-14 02:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classroom', '0005_alter_classroom_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='instructor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='instructor_classrooms', to=settings.AUTH_USER_MODEL),
        ),
    ]