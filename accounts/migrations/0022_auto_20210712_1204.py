# Generated by Django 3.1.2 on 2021-07-12 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_auto_20210315_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='status',
            field=models.CharField(choices=[('Resolved With Dispatch', 'Resolved With Dispatch'), ('Resolved no dispatch', 'Resolved no dispatch'), ('Resolved-NTF', 'Resolved-NTF'), ('Pending Dispatch', 'Pending Dispatch'), ('Supervisor escalation', 'Supervisor escalation'), ('Jira escalation', 'Jira escalation'), ('Avoidable Escalation', 'Avoidable Escalation'), ('Miscellaneous', 'Miscellaneous'), ('Invalid VNN assigned', 'Invalid VNN assigned'), ('Number not assigned', 'Number not assigned'), ('Provisioning', 'Provisioning'), ('Enable secure plus', 'Enable secure plus'), ('Remove eero secure plus', 'Remove eero secure plus'), ('Eero secure plus not active', 'Eero secure plus not active')], max_length=500, null=True),
        ),
    ]
