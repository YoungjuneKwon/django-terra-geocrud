# Generated by Django 2.2.5 on 2019-09-28 10:47

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terra_geocrud', '0020_auto_20190927_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='crudview',
            name='default_list_properties',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=250), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='crudview',
            name='ui_schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, help_text='Custom ui:schema style for this entry.\n                                         https://react-jsonschema-form.readthedocs.io/en/latest/form-customization/'),
        ),
    ]
