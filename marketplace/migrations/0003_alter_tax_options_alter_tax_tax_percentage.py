# Generated by Django 4.2 on 2023-05-16 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_tax'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tax',
            options={'verbose_name_plural': 'Taxes'},
        ),
        migrations.AlterField(
            model_name='tax',
            name='tax_percentage',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Tax percentage(%)'),
        ),
    ]
