from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import Author, Book
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class SkipIndexFieldTests(TypesenseCollectionTestCase):
    """Tests for skipping indexing fields."""

    def test_unindexed_field(self) -> None:
        """Test that it can handle unindexed fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Author,
            skip_index_fields={
                Author._meta.get_field('name'),
            },
        )

        self.assertEqual(collection.name, 'author')
        self.assertEqual(
            collection.index_fields,
            {
                Author._meta.get_field('birth_date'),
                Author._meta.get_field('email'),
            },
        )
        self.assertEqual(
            collection.skip_index_fields,
            {
                Author._meta.get_field('name'),
            },
        )
        self.assertEqual(
            len(collection.index_fields)
            + len(collection.skip_index_fields)
            + len(collection.parents)
            + len(collection.children)
            + 1,  # plus one for the id
            len(Author._meta.get_fields()),
        )

    def test_unindexed_fields_in_index_fields(self) -> None:
        """Test that it raises if unindexed fields are included in index_fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Author,
                index_fields={
                    Author._meta.get_field('name'),
                },
                skip_index_fields={
                    Author._meta.get_field('name'),
                },
            )

    def test_unindexed_fields_not_in_model(self) -> None:
        """Test that it warns if unindexed fields are not in the model."""
        mock_client_instance = self.mock_client()

        with self.assertWarns(UserWarning):
            collection = TypesenseCollection(
                client=mock_client_instance,
                model=Author,
                skip_index_fields={
                    Book._meta.get_field('title'),
                },
            )
            self.maxDiff = None

            self.assertEqual(
                collection.typesense_fields,
                [
                    {
                        'type': 'string',
                        'name': 'email',
                        'facet': False,
                        'optional': False,
                        'index': True,
                    },
                    {
                        'type': 'int64',
                        'name': 'birth_date',
                        'facet': False,
                        'optional': False,
                        'index': True,
                    },
                    {
                        'type': 'string',
                        'name': 'title',
                        'facet': False,
                        'optional': False,
                        'index': False,
                    },
                    {
                        'type': 'string',
                        'name': 'name',
                        'facet': False,
                        'optional': False,
                        'index': True,
                    },
                ],
            )
