# Generated by Django 2.2.8 on 2019-12-04 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('terra_geocrud', '0033_extralayerstyle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extralayerstyle',
            name='layer_extra_geom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='styles', to='geostore.LayerExtraGeom'),
        ),
    ]
