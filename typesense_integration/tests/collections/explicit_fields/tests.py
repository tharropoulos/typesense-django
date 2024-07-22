from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import (
    Author,
    Book,
    Chapter,
    InvalidField,
)
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class ExplicitFieldTests(TypesenseCollectionTestCase):
    """Tests for explicit fields."""

    def test_explicit_index_fields(self) -> None:
        """Test explicit index fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            index_fields={
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(collection.parents, set())

    def test_explicit_parents(self) -> None:
        """Test explicit parents."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            parents={Book._meta.get_field('author')},
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            set(),
        )
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            set(),
        )

    def test_explicit_children(self) -> None:
        """Test explicit children."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            children={Book._meta.get_field('chapter')},
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            set(),
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )

    def test_reference_in_index_fields(self) -> None:
        """Test that it raises if a reference is included in index_fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('author'),
                },
            )

    def test_wrong_reference(self) -> None:
        """Test that it raises if a reference is not in the model's foreign key fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('author'),
                },
                parents={Author._meta.get_field('name')},  # type: ignore[arg-type]
            )

    def test_wrong_referenced_by(self) -> None:
        """Test that it raises if a referenced_by is not in another model's foreign keys."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('author'),
                },
                children={Author._meta.get_field('name')},  # type: ignore[arg-type]
            )

    def test_ignore_duplicate_names(self) -> None:
        """Test that it ignores if there are duplicate field names of the same model."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            index_fields={
                Book._meta.get_field('title'),
                Book._meta.get_field('title'),
            },
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {Book._meta.get_field('title')},
        )
        self.assertEqual(collection.parents, set())

    def test_raise_duplicate_names(self) -> None:
        """Test that it raises if there are duplicate field names of different models."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('title'),
                    Chapter._meta.get_field('title'),
                },
            )

    def test_invalid_model_attribute_type(self) -> None:
        """Test that it raises if a model attribute is not a field."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=InvalidField,
            )

    def test_valid_attribute_in_model_with_invalid(self) -> None:
        """Test that it doesn't raise if the attributes passed are valid."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=InvalidField,
            index_fields={
                InvalidField._meta.get_field('valid_type'),
            },
        )

        self.assertEqual(collection.name, 'invalid_field')
        self.assertEqual(
            collection.index_fields,
            {InvalidField._meta.get_field('valid_type')},
        )

    def test_warn_foreign_field(self) -> None:
        """Test that it warns if a foreign field is included in index_fields."""
        mock_client_instance = self.mock_client()

        with self.assertWarns(UserWarning):
            collection = TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Chapter._meta.get_field('chapter_content'),
                },
                children={Book._meta.get_field('chapter')},
            )

            self.assertEqual(collection.name, 'book')
            self.assertEqual(
                collection.children,
                {Book._meta.get_field('chapter')},
            )
            self.assertEqual(collection.parents, set())
            self.assertEqual(
                collection.index_fields,
                {
                    Chapter._meta.get_field('chapter_content'),
                },
            )
