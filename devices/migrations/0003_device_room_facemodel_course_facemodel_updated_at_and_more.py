# Generated by Django 5.1.1 on 2025-01-19 19:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0004_attendance_device_alter_schedule_room_and_more"),
        ("common", "0001_initial"),
        ("courses", "0001_initial"),
        ("devices", "0002_alter_trainingimage_file_path"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="room",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="devices",
                to="common.room",
            ),
        ),
        migrations.AddField(
            model_name="facemodel",
            name="course",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="courses.course",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="facemodel",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="facescanlog",
            name="attendance",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="scan_logs",
                to="attendance.attendance",
            ),
        ),
        migrations.AlterField(
            model_name="facemodel",
            name="model_version",
            field=models.IntegerField(),
        ),
        migrations.AddIndex(
            model_name="facescanlog",
            index=models.Index(
                fields=["scan_time"], name="devices_fac_scan_ti_af099e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="facescanlog",
            index=models.Index(
                fields=["student", "course"], name="devices_fac_student_e443f5_idx"
            ),
        ),
    ]
