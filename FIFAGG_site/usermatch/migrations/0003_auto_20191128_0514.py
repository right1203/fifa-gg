# Generated by Django 2.2.7 on 2019-11-27 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermatch', '0002_auto_20191128_0456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='result',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='tddate',
            field=models.DateTimeField(null=True),
        ),
    ]
