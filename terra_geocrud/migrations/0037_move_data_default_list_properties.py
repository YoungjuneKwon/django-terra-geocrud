# Generated by Django 2.2.9 on 2020-01-28 14:14

from django.db import migrations, models
import django.db.models.deletion


def move_data_default_list(apps, schema_editor):
    # We can't import Layer models directly as it may be a newer
    # version than this migration expects. We use the historical version.
    CrudView = apps.get_model('terra_geocrud', 'CrudView')
    SchemaObject = apps.get_model('geostore', 'LayerSchemaProperty')
    for view in CrudView.objects.all():
        view.default_list_properties2.add(*SchemaObject.objects.filter(layer=view.layer,
                                                                       slug__in=view.default_list_properties))
        view.save()


class Migration(migrations.Migration):

    dependencies = [
        ('geostore', '0041_auto_20200128_1414'),
        ('terra_geocrud', '0036_auto_20191210_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='crudview',
            name='default_list_properties2',
            field=models.ManyToManyField(blank=True, help_text='Default list of properties for a view',
                                         related_name='crud_views', to='geostore.LayerSchemaProperty'),
        ),
        migrations.RunPython(move_data_default_list),
        migrations.RemoveField(
            model_name='crudview',
            name='default_list_properties',
        ),
        migrations.RenameField(
            model_name='crudview',
            old_name='default_list_properties2',
            new_name='default_list_properties',
        ),
    ]