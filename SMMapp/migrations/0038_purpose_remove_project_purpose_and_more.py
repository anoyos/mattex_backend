# Generated by Django 4.0.4 on 2022-08-01 05:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SMMapp', '0037_alter_submission_submission_reference_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purpose',
            fields=[
                ('purpose_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Purpose id')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('short_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Short name')),
            ],
        ),
        migrations.RemoveField(
            model_name='project',
            name='purpose',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='parent_document_number',
        ),
        migrations.RemoveField(
            model_name='title',
            name='no_of_submission',
        ),
        migrations.RemoveField(
            model_name='title',
            name='project_level_id',
        ),
        migrations.RemoveField(
            model_name='title',
            name='title',
        ),
        migrations.AddField(
            model_name='project',
            name='duplication_key',
            field=models.CharField(blank=True, choices=[('field_project_id', 'By Project Id'), ('field_submission_type', 'By Submission Type'), ('field_discipline_code', 'By Discipline Code'), ('field_year', 'By Year')], max_length=100, null=True, verbose_name='De-duplication key'),
        ),
        migrations.AddField(
            model_name='project',
            name='title_structure',
            field=models.JSONField(default={'structure': []}, verbose_name='Submission title structure'),
        ),
        migrations.AddField(
            model_name='submission',
            name='parent_system_id',
            field=models.CharField(default=1, editable=False, max_length=50, verbose_name='Parent System Id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='system_id',
            field=models.CharField(default=1, editable=False, max_length=50, verbose_name='System Id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='title',
            field=models.CharField(default=1, editable=False, max_length=255, verbose_name='Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='year',
            field=models.IntegerField(default=1, editable=False, verbose_name='Year'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='submission',
            name='document_number',
            field=models.IntegerField(verbose_name='Document number'),
        ),
        migrations.AddField(
            model_name='project',
            name='purposes',
            field=models.ManyToManyField(blank=True, null=True, related_name='purpose_projects', to='SMMapp.purpose'),
        ),
        migrations.AlterField(
            model_name='aboutthissubmission',
            name='purpose_chosen',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='purpose_chosen', to='SMMapp.purpose'),
            preserve_default=False,
        ),
    ]
