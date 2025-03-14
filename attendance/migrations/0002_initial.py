# Generated by Django 5.1.1 on 2024-12-03 15:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("attendance", "0001_initial"),
        ("courses", "0001_initial"),
        ("members", "__first__"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendance",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attendances",
                to="courses.course",
            ),
        ),
        migrations.AddField(
            model_name="attendance",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attendances",
                to="members.member",
            ),
        ),
        migrations.AddField(
            model_name="schedule",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="schedules",
                to="courses.course",
            ),
        ),
        migrations.AddField(
            model_name="attendance",
            name="schedule",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attendances",
                to="attendance.schedule",
            ),
        ),
    ]
