# Generated by Django 4.2 on 2023-05-01 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_userprofile_address_line_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='pin_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]