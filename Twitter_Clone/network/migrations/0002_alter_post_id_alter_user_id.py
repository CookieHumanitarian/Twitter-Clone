# Generated by Django 5.0.6 on 2024-08-29 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
