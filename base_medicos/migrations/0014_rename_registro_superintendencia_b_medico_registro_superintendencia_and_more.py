# Generated by Django 5.0.6 on 2024-12-21 00:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_medicos', '0013_rename_registro_superintendencia_medico_registro_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medico',
            old_name='registro_superintendencia_b',
            new_name='registro_superintendencia',
        ),
        migrations.RemoveField(
            model_name='medico',
            name='registro',
        ),
    ]
