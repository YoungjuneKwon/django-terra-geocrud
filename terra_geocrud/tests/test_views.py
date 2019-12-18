from tempfile import TemporaryDirectory

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from geostore import GeometryTypes
from geostore.models import Feature, LayerExtraGeom, FeatureExtraGeom
from rest_framework import status
from rest_framework.test import APITestCase
from terra_accounts.tests.factories import TerraUserFactory

from terra_geocrud.models import CrudViewProperty
from . import factories
from .settings import FEATURE_PROPERTIES, LAYER_SCHEMA
from .. import models, settings as app_settings
from ..properties.schema import sync_ui_schema


class CrudGroupViewSetTestCase(APITestCase):
    def setUp(self):
        self.group = models.CrudGroupView.objects.create(name="group", order=0)

    def test_list_endpoint(self):
        response = self.client.get(reverse('crudgroupview-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), models.CrudGroupView.objects.count())

        self.assertEqual(data[0]['id'], self.group.pk)

    def test_detail_endpoint(self):
        response = self.client.get(reverse('crudgroupview-detail', args=(self.group.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data['id'], self.group.pk)


class CrudViewSetTestCase(APITestCase):
    def setUp(self):
        self.group_1 = models.CrudGroupView.objects.create(name="group 1", order=0)
        self.group_2 = models.CrudGroupView.objects.create(name="group 2", order=1)
        self.view_1 = factories.CrudViewFactory(name="View 1", order=0, group=self.group_1)
        self.view_2 = factories.CrudViewFactory(name="View 2", order=0, group=self.group_2)
        self.view_3 = factories.CrudViewFactory(name="View 3", order=1, group=self.group_2)
        self.extra_layer = LayerExtraGeom.objects.create(geom_type=GeometryTypes.MultiPolygon,
                                                         title='extra geom 1',
                                                         layer=self.view_1.layer)

    def test_list_endpoint(self):
        response = self.client.get(reverse('crudview-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), models.CrudView.objects.count())

        self.assertEqual(data[0]['id'], self.view_1.pk)

    def test_detail_endpoint(self):
        response = self.client.get(reverse('crudview-detail', args=(self.view_1.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data['id'], self.view_1.pk)

    def test_default_point_style(self):
        crud_view = factories.CrudViewFactory(layer__geom_type=GeometryTypes.Point)
        response = self.client.get(reverse('crudview-detail', args=(crud_view.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['map_style'], app_settings.TERRA_GEOCRUD['STYLES']['point'])

    def test_override_point_style(self):
        custom_style = {
            'type': 'circle',
            'paint': {
                'circle-color': '#FFFFFF',
                'circle-radius': 25
            }
        }
        crud_view = factories.CrudViewFactory(layer__geom_type=GeometryTypes.MultiPoint,
                                              map_style=custom_style)
        response = self.client.get(reverse('crudview-detail', args=(crud_view.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['map_style'], custom_style)

    def test_default_line_style(self):
        crud_view = factories.CrudViewFactory(layer__geom_type=GeometryTypes.LineString)
        response = self.client.get(reverse('crudview-detail', args=(crud_view.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['map_style'], app_settings.TERRA_GEOCRUD['STYLES']['line'])

    def test_override_line_style(self):
        custom_style = {
            'type': 'line',
            'paint': {
                'line-color': '#000',
                'line-width': 3
            }
        }
        crud_view = factories.CrudViewFactory(layer__geom_type=GeometryTypes.MultiLineString,
                                              map_style=custom_style)
        response = self.client.get(reverse('crudview-detail', args=(crud_view.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['map_style'], custom_style)

    def test_default_polygon_style(self):
        crud_view = factories.CrudViewFactory(layer__geom_type=GeometryTypes.Polygon)
        response = self.client.get(reverse('crudview-detail', args=(crud_view.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['map_style'], app_settings.TERRA_GEOCRUD['STYLES']['polygon'])

    def test_override_polygon_style(self):
        custom_style = {
            'type': 'fill',
            'paint': {
                'fill-color': '#000'
            }
        }
        crud_view = factories.CrudViewFactory(layer__geom_type=GeometryTypes.MultiPolygon,
                                              map_style=custom_style)
        response = self.client.get(reverse('crudview-detail', args=(crud_view.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['map_style'], custom_style)

    def test_original_ui_schema(self):
        response = self.client.get(reverse('crudview-detail', args=(self.view_1.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(data['ui_schema'], self.view_1.ui_schema, data)

    def test_grouped_ui_schema(self):
        group_1 = models.FeaturePropertyDisplayGroup.objects.create(crud_view=self.view_1, label='test')
        group_2 = models.FeaturePropertyDisplayGroup.objects.create(crud_view=self.view_1, label='test2')
        CrudViewProperty.objects.create(view=self.view_1, key="name",
                                        group=group_2,
                                        json_schema={'type': "string", "title": "Name"},
                                        ui_schema={'ui:widget': 'textarea'})
        CrudViewProperty.objects.create(view=self.view_1, key="age",
                                        group=group_1,
                                        json_schema={'type': "integer", "title": "Age"})
        CrudViewProperty.objects.create(view=self.view_1, key="country",
                                        json_schema={'type': "string", "title": "Country"})
        sync_ui_schema(self.view_1)
        response = self.client.get(reverse('crudview-detail', args=(self.view_1.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertDictEqual(
            data['ui_schema'],
            {'ui:order': ['test', 'test2', '*'],
             'test': {'ui:order': ['*']},
             'test2': {'ui:order': ['*'],
                       'name': {'ui:widget': 'textarea'}}}
        )
        group_1.delete()
        group_2.delete()


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class CrudSettingsViewTestCase(TestCase):
    def setUp(self):
        self.group_1 = models.CrudGroupView.objects.create(name="group 1", order=0)
        self.group_2 = models.CrudGroupView.objects.create(name="group 2", order=1)
        self.view_1 = factories.CrudViewFactory(name="View 1", order=0, group=self.group_1)
        self.view_2 = factories.CrudViewFactory(name="View 2", order=0, group=self.group_2)
        self.view_3 = factories.CrudViewFactory(name="View 3", order=1, group=self.group_2)
        self.response = self.client.get(reverse('settings'))

    def test_endpoint_access(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_endpoint_menu(self):
        """
        Menu has 1 section per group, and 1 section for non grouped views
        """
        data = self.response.json()
        self.assertEqual(len(data['menu']), models.CrudGroupView.objects.count() + 1)


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class CrudRenderPointTemplateDetailViewTestCase(APITestCase):
    def setUp(self):
        self.crud_view = factories.CrudViewFactory(name="Composantes", order=0,
                                                   layer__schema=LAYER_SCHEMA,
                                                   layer__geom_type=GeometryTypes.Point)
        self.extra_layer = LayerExtraGeom.objects.create(geom_type=GeometryTypes.MultiPolygon,
                                                         title='extra geom 1',
                                                         layer=self.crud_view.layer)

        self.feature = Feature.objects.create(
            layer=self.crud_view.layer,
            geom=Point(x=-0.246322800072846, y=44.5562461167907),
            properties=FEATURE_PROPERTIES,
        )
        self.template = factories.TemplateDocxFactory.create(
            name='Template',
        )
        self.crud_view.templates.add(self.template)

    def test_template_rendering(self):
        response = self.client.get(
            reverse(
                'feature-generate-template',
                args=(self.feature.layer.pk, self.feature.identifier, self.template.pk)
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers['content-type'][-1],
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class CrudFeatureViewsSetTestCase(APITestCase):
    def setUp(self):
        self.crud_view = factories.CrudViewFactory()
        # add extra geometries to layer
        self.extra_layer_1 = LayerExtraGeom.objects.create(
            layer=self.crud_view.layer,
            geom_type=GeometryTypes.Point,
            title='Extra 1'
        )
        self.extra_layer_2 = LayerExtraGeom.objects.create(
            layer=self.crud_view.layer,
            geom_type=GeometryTypes.LineString,
            title='Extra 2'
        )
        self.group_1 = models.FeaturePropertyDisplayGroup.objects.create(crud_view=self.crud_view, label='test')
        self.group_2 = models.FeaturePropertyDisplayGroup.objects.create(crud_view=self.crud_view, label='test2')

        CrudViewProperty.objects.create(view=self.crud_view, key="name",
                                        group=self.group_2,
                                        json_schema={'type': "string", "title": "Name"})
        CrudViewProperty.objects.create(view=self.crud_view, key="age",
                                        group=self.group_1,
                                        json_schema={'type': "integer", "title": "Age"})
        CrudViewProperty.objects.create(view=self.crud_view, key="country",
                                        json_schema={'type': "string", "title": "Country"})

        self.feature = Feature.objects.create(geom=Point(0, 0, srid=4326),
                                              properties={
                                                  "age": 10,
                                                  "name": "2012-01-01",
                                                  "country": "slovenija"},
                                              layer=self.crud_view.layer)
        # add extra geometries to feature
        self.extra_feature = FeatureExtraGeom.objects.create(
            feature=self.feature,
            layer_extra_geom=self.extra_layer_1,
            geom='POINT(0 0)'
        )
        self.pictures = factories.FeaturePictureFactory.create_batch(10, feature=self.feature)
        self.attachments = factories.FeatureAttachmentFactory.create_batch(10, feature=self.feature)
        self.template = factories.TemplateDocxFactory()
        self.crud_view.templates.add(self.template)
        self.user = TerraUserFactory()
        self.client.force_authenticate(self.user)

    def test_list_endpoint(self):
        response_list = self.client.get(reverse('feature-list', args=(self.crud_view.layer_id,)),
                                        format="json")
        data = response_list.json()
        self.assertEqual(len(data['results']), self.crud_view.layer.features.count(), data)

    def test_property_detail_display_with_groups(self):
        response_detail = self.client.get(reverse('feature-detail',
                                                  args=(self.crud_view.layer_id,
                                                        self.feature.identifier)),
                                          format="json")
        data = response_detail.json()
        expected_keys = list(self.crud_view.feature_display_groups.all()
                             .values_list('slug', flat=True)) + ['__default__']
        self.assertEqual(list(data['display_properties'].keys()), expected_keys)

    def test_property_detail_documents(self):
        response_detail = self.client.get(reverse('feature-detail',
                                                  args=(self.crud_view.layer_id,
                                                        self.feature.identifier)),
                                          format="json")
        data = response_detail.json()
        self.assertEqual(len(data['documents']), self.crud_view.templates.count())

    def test_create_grouped_properties(self):
        """ Test creation with grouped properties """
        data = {"geom": "POINT(0 0)",
                "properties": {
                    "test2": {"name": "toto"},
                    "test": {"age": 10},
                    "country": "France"
                }}

        response = self.client.post(reverse('feature-list',
                                            args=(self.crud_view.layer_id, )),
                                    data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        json_data = response.json()

        # feature properties are grouped in api
        self.assertDictEqual(json_data['properties'], data['properties'])

        # feature properties are not grouped in object
        feature = Feature.objects.get(pk=json_data['id'])
        self.assertDictEqual(feature.properties, {"name": "toto",
                                                  "age": 10,
                                                  "country": "France"})

    def test_attachment_endpoint(self):
        response = self.client.get(reverse('attachment-list',
                                           args=(self.feature.identifier, )))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_picture_endpoint(self):
        response = self.client.get(reverse('picture-list',
                                           args=(self.feature.identifier, )))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
