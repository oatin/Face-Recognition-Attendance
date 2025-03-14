# Generated by Django 5.1.1 on 2024-12-08 17:58

import devices.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("devices", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trainingimage",
            name="file_path",
            field=models.ImageField(
                upload_to=devices.models.training_image_upload_path
            ),
        ),
    ]
