# Generated by Django 5.0.7 on 2024-08-29 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0002_alter_associated_validators_apikey_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='associated_validators',
            name='apikey',
            field=models.TextField(),
        ),
    ]
