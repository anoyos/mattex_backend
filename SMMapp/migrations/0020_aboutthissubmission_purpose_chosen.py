# Generated by Django 4.0.4 on 2022-07-15 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SMMapp', '0019_alter_aboutthissubmission_purpose_of_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutthissubmission',
            name='purpose_chosen',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
