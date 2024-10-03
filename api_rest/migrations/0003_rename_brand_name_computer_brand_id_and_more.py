# Generated by Django 5.1.1 on 2024-09-18 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0002_historialcomputer_updated_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='computer',
            old_name='brand_name',
            new_name='brand_id',
        ),
        migrations.RenameField(
            model_name='computer',
            old_name='location_name',
            new_name='location_id',
        ),
        migrations.RenameField(
            model_name='computer',
            old_name='model_name',
            new_name='model_id',
        ),
        migrations.RenameField(
            model_name='computer',
            old_name='organization_name',
            new_name='organization_id',
        ),
        migrations.RenameField(
            model_name='computer',
            old_name='os_version_name',
            new_name='os_version_id',
        ),
        migrations.RenameField(
            model_name='computer',
            old_name='osfamily_name',
            new_name='osfamily_id',
        ),
        migrations.RenameField(
            model_name='historialcomputer',
            old_name='brand_name',
            new_name='brand_id',
        ),
        migrations.RenameField(
            model_name='historialcomputer',
            old_name='location_name',
            new_name='location_id',
        ),
        migrations.RenameField(
            model_name='historialcomputer',
            old_name='model_name',
            new_name='model_id',
        ),
        migrations.RenameField(
            model_name='historialcomputer',
            old_name='organization_name',
            new_name='organization_id',
        ),
        migrations.RenameField(
            model_name='historialcomputer',
            old_name='os_version_name',
            new_name='os_version_id',
        ),
        migrations.RenameField(
            model_name='historialcomputer',
            old_name='osfamily_name',
            new_name='osfamily_id',
        ),
    ]
