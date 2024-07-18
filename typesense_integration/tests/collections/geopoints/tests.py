from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import GeoPoint
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class GeopointTests(TypesenseCollectionTestCase):
    """Tests for geopoints."""

    def test_geopoint_in_index_fields(self) -> None:
        """Test that it raises if a geopoint is included in index_fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=GeoPoint,
                index_fields={
                    GeoPoint._meta.get_field('lat'),
                },
                geopoints={
                    (GeoPoint._meta.get_field('lat'), GeoPoint._meta.get_field('long')),
                },
            )

    def test_geopoints(self) -> None:
        """Test that it can handle geopoints."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=GeoPoint,
            index_fields={
                GeoPoint._meta.get_field('name'),
            },
            geopoints={
                (GeoPoint._meta.get_field('lat'), GeoPoint._meta.get_field('long')),
            },
        )

        self.assertEqual(collection.name, 'geo_point')
        self.assertEqual(
            collection.index_fields,
            {
                GeoPoint._meta.get_field('name'),
            },
        )
        self.assertEqual(
            collection.geopoints,
            {(GeoPoint._meta.get_field('lat'), GeoPoint._meta.get_field('long'))},
        )

    def test_geopoints_not_float(self) -> None:
        """Test that it raises if a geopoint is not a float."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=GeoPoint,
                geopoints={
                    (GeoPoint._meta.get_field('lat'), GeoPoint._meta.get_field('name')),  # type: ignore[arg-type]
                },
            )

    def test_geopoints_not_tuple(self) -> None:
        """Test that it raises if a geopoint is not a tuple."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(TypeError):
            TypesenseCollection(
                client=mock_client_instance,
                model=GeoPoint,
                geopoints={
                    GeoPoint._meta.get_field('lat'),  # type: ignore[arg-type]
                },
            )
