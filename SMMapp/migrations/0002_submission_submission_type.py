# Generated by Django 4.0.4 on 2022-07-05 07:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SMMapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='submission_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='submission_type', to='SMMapp.submissiontype'),
            preserve_default=False,
        ),
    ]
