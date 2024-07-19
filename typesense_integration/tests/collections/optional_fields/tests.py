from __future__ import annotations

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import OptionalFields
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class OptionalFieldTests(TypesenseCollectionTestCase):
    """Tests for optional fields."""

    def test_optional_field(self) -> None:
        """Test that it can handle optional fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=OptionalFields,
            index_fields={
                OptionalFields._meta.get_field('optional'),
            },
        )

        self.assertEqual(collection.name, 'optional_fields')

        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'optional',
                    'type': 'string',
                    'facet': False,
                    'optional': True,
                    'index': True,
                },
            ],
        )

    def test_optional_geopoint_both(self) -> None:
        """Test that it can handle both optional geopoint fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=OptionalFields,
            geopoints={
                (
                    OptionalFields._meta.get_field('optional_lat'),
                    OptionalFields._meta.get_field('optional_long'),
                ),
            },
        )

        self.assertEqual(collection.name, 'optional_fields')

        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'optional_lat_optional_long',
                    'type': 'geopoint',
                    'facet': False,
                    'optional': True,
                    'index': True,
                },
            ],
        )

    def test_optional_geopoint_one(self) -> None:
        """Test that it can handle one optional geopoint field."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=OptionalFields,
            geopoints={
                (
                    OptionalFields._meta.get_field('required_lat'),
                    OptionalFields._meta.get_field('optional_long'),
                ),
            },
        )

        self.assertEqual(collection.name, 'optional_fields')

        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'required_lat_optional_long',
                    'type': 'geopoint',
                    'facet': False,
                    'optional': True,
                    'index': True,
                },
            ],
        )

    def test_optional_relation_join(self) -> None:
        """Test that it can handle one optional relation field with join."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=OptionalFields,
            parents={
                OptionalFields._meta.get_field('optional_ref'),
            },
            use_joins=True,
        )

        self.assertEqual(collection.name, 'optional_fields')

        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'optional_ref_id',
                    'type': 'string',
                    'facet': False,
                    'optional': True,
                    'index': True,
                    'reference': 'reference.id',
                },
            ],
        )

    def test_optional_relation_detailed(self) -> None:
        """Test that it can handle one optional detailed relation field."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=OptionalFields,
            parents={
                OptionalFields._meta.get_field('optional_ref'),
            },
            detailed_parents=True,
        )

        self.assertEqual(collection.name, 'optional_fields')

        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'optional_ref',
                    'type': 'object',
                    'facet': False,
                    'optional': True,
                    'index': True,
                },
            ],
        )
