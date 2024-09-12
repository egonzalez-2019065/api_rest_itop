# Generated by Django 5.1.1 on 2024-09-11 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistedAccessToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='computer',
            name='hostname',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
