# Generated by Django 3.1.2 on 2021-02-05 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20210127_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='secure_Plus_Checker',
            field=models.CharField(choices=[('Eero Secure Plus Enabled', 'Eero Secure Plus Enabled'), ('Cannot activate Secure Plus', 'Cannot activate Secure Plus')], max_length=500, null=True),
        ),
    ]
