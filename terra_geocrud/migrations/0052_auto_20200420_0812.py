# Generated by Django 3.0.5 on 2020-04-20 08:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import geostore.validators


class Migration(migrations.Migration):

    dependencies = [
        ('terra_geocrud', '0051_auto_20200420_0751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crudviewproperty',
            name='json_schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, validators=[geostore.validators.validate_json_schema]),
        ),
    ]
