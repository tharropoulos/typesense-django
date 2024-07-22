from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import MultipleSortableFields
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class SortingFieldsTests(TypesenseCollectionTestCase):
    """Tests for sorting fields."""

    def test_no_fields_mentioned(self) -> None:
        """Test no fields mentioned."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=MultipleSortableFields,
        )

        relevant_fields = [
            {'name': field['name'], 'type': field['type'], 'sort': field['sort']}
            for field in collection.typesense_fields
        ]

        self.assertEqual(
            relevant_fields,
            [
                {
                    'name': 'second',
                    'type': 'int64',
                    'sort': True,
                },
                {'name': 'name', 'type': 'string', 'sort': False},
                {
                    'name': 'first',
                    'type': 'int32',
                    'sort': True,
                },
            ],
        )

    def test_all_fields_all_fields(self) -> None:
        """Test all field sortable."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=MultipleSortableFields,
            sorting_fields=True,
        )

        relevant_fields = [
            {'name': field['name'], 'type': field['type'], 'sort': field['sort']}
            for field in collection.typesense_fields
        ]

        self.assertEqual(
            relevant_fields,
            [
                {
                    'name': 'second',
                    'type': 'int64',
                    'sort': True,
                },
                {'name': 'name', 'type': 'string', 'sort': True},
                {
                    'name': 'first',
                    'type': 'int32',
                    'sort': True,
                },
            ],
        )

    def test_all_fields_explicit_fields(self) -> None:
        """Test all field sortable."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=MultipleSortableFields,
            sorting_fields={
                MultipleSortableFields._meta.get_field('name'),
            },
        )

        relevant_fields = [
            {'name': field['name'], 'type': field['type'], 'sort': field['sort']}
            for field in collection.typesense_fields
        ]

        self.assertEqual(
            relevant_fields,
            [
                {
                    'name': 'second',
                    'type': 'int64',
                    'sort': False,
                },
                {'name': 'name', 'type': 'string', 'sort': True},
                {
                    'name': 'first',
                    'type': 'int32',
                    'sort': False,
                },
            ],
        )

    def test_raises_fields_not_in_index(self) -> None:
        """Test that it raises if sorting field is not in indexed fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=MultipleSortableFields,
                skip_index_fields={MultipleSortableFields._meta.get_field('name')},
                sorting_fields={
                    MultipleSortableFields._meta.get_field('name'),
                },
            )
