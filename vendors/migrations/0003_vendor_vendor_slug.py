# Generated by Django 4.2 on 2023-05-02 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0002_alter_vendor_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='vendor_slug',
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]