# Generated by Django 3.1.2 on 2020-12-22 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20201222_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='source',
            field=models.CharField(choices=[('Install', 'Install'), ('No schedule Trouble', 'No schedule Trouble'), ('DDT Pending Provisioning', 'DDT Pending Provisioning'), ('Email Chain', 'Email Chain'), ('Fision Enterprise', 'Fision Enterprise'), ('Disco/Reco', 'Disco/Reco'), ('Project', 'Project'), ('Collections', 'Collections'), ('Miscellaneous', 'Miscellaneous'), ('Inbound Tech Call', 'Inbound Tech Call'), ('Inbound Account Manager', 'Inbound Account Manager'), ('Inbound CS Agent', 'Inbound CS Agent'), ('Salisbury Gen tech support', 'Salisbury Gen tech support'), ('Fiber support', 'Fiber support'), ('change orders/disconnects/reconnects', 'change orders/disconnects/reconnects')], max_length=500, null=True),
        ),
    ]
