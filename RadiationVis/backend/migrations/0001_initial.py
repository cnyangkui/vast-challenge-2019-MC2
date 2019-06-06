# Generated by Django 2.2.1 on 2019-06-06 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MobileSensorReadings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('sid', models.IntegerField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('value', models.FloatField(blank=True, null=True)),
                ('units', models.CharField(blank=True, max_length=45, null=True)),
                ('uid', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'mobilesensorreadings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StaticSensorLocations',
            fields=[
                ('sid', models.IntegerField(primary_key=True, serialize=False)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'staticsensorlocations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StaticSensorReadings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('value', models.FloatField(blank=True, null=True)),
                ('units', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'staticsensorreadings',
                'managed': False,
            },
        ),
    ]
