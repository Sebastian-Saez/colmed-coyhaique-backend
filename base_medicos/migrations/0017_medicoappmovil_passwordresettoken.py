# Generated by Django 5.0.6 on 2025-02-13 21:09

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_medicos', '0016_remove_registrosuperintendencia_codigo_validacion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicoAppMovil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inscripcion', models.DateTimeField(auto_now=True)),
                ('contraseña', models.CharField(max_length=200)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_medicos.medico')),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used', models.BooleanField(default=False)),
                ('medico_app_movil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_medicos.medicoappmovil')),
            ],
        ),
    ]
