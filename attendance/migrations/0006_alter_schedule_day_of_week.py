# Generated by Django 5.1.1 on 2025-02-02 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "attendance",
            "0005_alter_attendance_course_alter_attendance_schedule_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="schedule",
            name="day_of_week",
            field=models.CharField(
                choices=[
                    ("monday", "Monday"),
                    ("tuesday", "Tuesday"),
                    ("wednesday", "Wednesday"),
                    ("thursday", "Thursday"),
                    ("friday", "Friday"),
                    ("saturday", "Saturday"),
                    ("sunday", "Sunday"),
                ],
                max_length=10,
            ),
        ),
    ]
