# Generated by Django 5.0.6 on 2024-10-29 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_colmed', '0004_alter_entidad_nombre_entidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficio',
            name='titulo',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='beneficio',
            name='descripcion',
            field=models.TextField(),
        ),
    ]
