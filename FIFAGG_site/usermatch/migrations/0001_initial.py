# Generated by Django 2.2.7 on 2019-11-27 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matchid', models.CharField(max_length=200)),
                ('result', models.IntegerField()),
                ('tddate', models.DateField()),
                ('loadingtime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
