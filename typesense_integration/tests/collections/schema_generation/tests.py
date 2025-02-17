from __future__ import annotations

from django.conf import settings
from django.test import TestCase
from typesense import Client
from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import (
    Book,
    GeoPoint,
    MultipleSortableFields,
    OptionalFields,
    Reader,
    VerboseName,
    VerboseRelation,
)


class SchemaGenerationTests(TestCase):
    """Tests for schema generation."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.typesense_client = Client(
            {
                'nodes': [
                    {
                        'host': settings.TYPESENSE_HOST,
                        'port': settings.TYPESENSE_PORT,
                        'protocol': settings.TYPESENSE_PROTOCOL,
                    },
                ],
                'api_key': settings.TYPESENSE_API_KEY,
                'connection_timeout_seconds': 2,
            },
        )
        self.maxDiff = None
        self.collections = self.typesense_client.collections.retrieve()
        for collection in self.collections:
            self.typesense_client.collections[collection['name']].delete()

    def test_generate_schema(self) -> None:
        """Test Schema Generation."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_override_id(self) -> None:
        """Test Schema Generation."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            override_id=True,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'type': 'string',
                        'name': 'title',
                        'facet': False,
                        'index': True,
                        'optional': False,
                        'infix': False,
                        'locale': '',
                        'sort': False,
                        'stem': False,
                    },
                    {
                        'type': 'int64',
                        'name': 'published_date',
                        'facet': False,
                        'index': True,
                        'optional': False,
                        'infix': False,
                        'locale': '',
                        'sort': True,
                        'stem': False,
                    },
                    {
                        'type': 'string',
                        'name': 'id',
                        'facet': False,
                        'index': True,
                        'optional': False,
                        'infix': False,
                        'locale': '',
                        'sort': True,
                        'stem': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_with_joins(self) -> None:
        """Test Schema Generation."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            use_joins=True,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                        'reference': 'author.id',
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'author_id',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                        'reference': 'author.id',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_detailed_relations(self) -> None:
        """Test Schema Generation."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            detailed_children=True,
            detailed_parents=True,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'enable_nested_fields': True,
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author',
                        'type': 'object',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'chapter',
                        'type': 'object[]',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': True,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': True,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'index': True,
                        'infix': False,
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'author',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'object',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'chapter',
                        'optional': True,
                        'sort': False,
                        'stem': False,
                        'type': 'object[]',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_email(self) -> None:
        """Test generating schema with an email field."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Reader,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'reader',
                'fields': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'email',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'birth_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
                'token_separators': ['+', '-', '@', '.'],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'name',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'email',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'index': True,
                        'infix': False,
                        'name': 'birth_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'reader',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': ['+', '-', '@', '.'],
            },
        )

        self.typesense_client.collections['reader'].delete()

    def test_generate_schema_verbose_name(self) -> None:
        """Test generating schema with an email field."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=VerboseName,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'custom_name',
                'fields': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'name',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                ],
                'name': 'custom_name',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['custom_name'].delete()

    def test_generate_schema_verbose_relation(self) -> None:
        """Test generating schema with an email field."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            use_joins=True,
            detailed_parents=True,
            detailed_children=True,
            model=VerboseRelation,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'verbose_relation',
                'enable_nested_fields': True,
                'fields': [
                    {
                        'name': 'custom_name_id',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                        'reference': 'custom_name.id',
                    },
                    {
                        'name': 'custom_name',
                        'type': 'object',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': True,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'custom_name_id',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                        'reference': 'custom_name.id',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'custom_name',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'object',
                    },
                ],
                'name': 'verbose_relation',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['verbose_relation'].delete()

    def test_generate_schema_facet_all(self) -> None:
        """Test Schema Generation with facets on all fields."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            use_joins=True,
            facets=True,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': True,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': True,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': True,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'reference': 'author.id',
                        'optional': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': True,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                    {
                        'facet': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'author_id',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                        'reference': 'author.id',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_facet_some(self) -> None:
        """Test Schema Generation with facets on some fields."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            use_joins=True,
            detailed_parents=True,
            facets={Book._meta.get_field('author')},
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': True,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                        'reference': 'author.id',
                    },
                    {
                        'name': 'author',
                        'type': 'object',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
                'enable_nested_fields': True,
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': True,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'sort': True,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                    {
                        'facet': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'author_id',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                        'reference': 'author.id',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'author',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'object',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_skip_fields(self) -> None:
        """Test Schema Generation while skipping some fields."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            skip_index_fields={
                Book._meta.get_field('published_date'),
                Book._meta.get_field('author'),
            },
            detailed_parents=True,
            use_joins=True,
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': False,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': False,
                        'optional': False,
                        'reference': 'author.id',
                    },
                    {
                        'name': 'author',
                        'type': 'object',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': False,
                        'optional': False,
                    },
                ],
                'enable_nested_fields': True,
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': True,
                'fields': [
                    {
                        'facet': False,
                        'infix': False,
                        'index': True,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'index': False,
                        'infix': False,
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                    {
                        'facet': False,
                        'index': False,
                        'infix': False,
                        'locale': '',
                        'name': 'author_id',
                        'optional': False,
                        'reference': 'author.id',
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'index': False,
                        'infix': False,
                        'locale': '',
                        'name': 'author',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'object',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_default_sorting_field(self) -> None:
        """Test Schema Generation while defining a default sorting field."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            default_sorting_field=Book._meta.get_field('published_date'),
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
                'default_sorting_field': 'published_date',
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': 'published_date',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_generate_schema_geopoints(self) -> None:
        """Test Schema Generation while having geopoints some fields."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=GeoPoint,
            index_fields={
                GeoPoint._meta.get_field('name'),
            },
            geopoints={
                (GeoPoint._meta.get_field('lat'), GeoPoint._meta.get_field('long')),
            },
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'geo_point',
                'fields': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'lat_long',
                        'type': 'geopoint',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                    },
                    {
                        'name': 'lat_long',
                        'type': 'geopoint',
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'optional': False,
                        'stem': False,
                    },
                ],
                'name': 'geo_point',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['geo_point'].delete()

    def test_generate_schema_optional_fields(self) -> None:
        """Test Schema Generation."""
        collection = TypesenseCollection(
            client=self.typesense_client,
            model=OptionalFields,
            index_fields={
                OptionalFields._meta.get_field('optional'),
            },
        )

        schema = collection.generate_schema()

        actual = collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'optional_fields',
                'fields': [
                    {
                        'name': 'optional',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': True,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'optional',
                        'optional': True,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                ],
                'name': 'optional_fields',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['optional_fields'].delete()

    def test_generate_schema_explicit_sorting_fields(self) -> None:
        """Test Schema Generation with explicit sorting fields."""
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            sorting_fields={
                Book._meta.get_field('published_date'),
                Book._meta.get_field('title'),
            },
        )

        schema = original_collection.generate_schema()

        actual = original_collection.create()

        self.assertEqual(
            schema,
            {
                'name': 'book',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'sort': True,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': False,
                    },
                ],
            },
        )

        actual.pop('created_at')
        self.assertEqual(
            actual,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': True,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_update_schema(self) -> None:
        """Test Schema Update."""
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
        )

        original_on_server = original_collection.create()

        created_at = original_on_server.get('created_at')
        original_on_server.pop('created_at')

        self.assertEqual(
            original_on_server,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].documents.create(
            {
                'title': 'The Great Gatsby',
                'published_date': 1925,
            },
        )

        updated_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            index_fields={
                Book._meta.get_field('published_date'),
            },
        )

        updated_collection.update()

        updated_on_server = self.typesense_client.collections['book'].retrieve()

        self.assertEqual(
            updated_on_server,
            {
                'created_at': created_at,
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 1,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_update_schema_with_default_sorting_field(self) -> None:
        """
        Test Schema Update with change to the default sorting field.

        It should warn the user as updating the schema only allows for field changes, and
        not change the default sorting field
        """
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=MultipleSortableFields,
            default_sorting_field=MultipleSortableFields._meta.get_field('first'),
        )

        original_on_server = original_collection.create()

        created_at = original_on_server.get('created_at')
        original_on_server.pop('created_at')

        self.assertEqual(
            original_on_server,
            {
                'default_sorting_field': 'first',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'second',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'name',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'first',
                        'optional': False,
                        'sort': True,
                        'stem': False,
                        'type': 'int32',
                    },
                ],
                'name': 'multiple_sortable_fields',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['multiple_sortable_fields'].documents.create(
            {'first': 32, 'second': 200, 'name': 'test'},
        )

        updated_collection = TypesenseCollection(
            client=self.typesense_client,
            model=MultipleSortableFields,
            default_sorting_field=MultipleSortableFields._meta.get_field('second'),
        )

        with self.assertWarns(UserWarning):
            updated_collection.update()
            updated_on_server = self.typesense_client.collections[
                'multiple_sortable_fields'
            ].retrieve()

            self.assertEqual(
                updated_on_server,
                {
                    'created_at': created_at,
                    'default_sorting_field': 'first',
                    'enable_nested_fields': False,
                    'fields': [
                        {
                            'facet': False,
                            'sort': True,
                            'index': True,
                            'infix': False,
                            'locale': '',
                            'name': 'second',
                            'optional': False,
                            'stem': False,
                            'type': 'int64',
                        },
                        {
                            'facet': False,
                            'index': True,
                            'infix': False,
                            'locale': '',
                            'name': 'name',
                            'optional': False,
                            'sort': False,
                            'stem': False,
                            'type': 'string',
                        },
                        {
                            'facet': False,
                            'index': True,
                            'infix': False,
                            'locale': '',
                            'name': 'first',
                            'optional': False,
                            'sort': True,
                            'stem': False,
                            'type': 'int32',
                        },
                    ],
                    'name': 'multiple_sortable_fields',
                    'num_documents': 1,
                    'symbols_to_index': [],
                    'token_separators': [],
                },
            )

    def test_update_schema_skip_index_fields(self) -> None:
        """Test Schema Update."""
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            default_sorting_field=Book._meta.get_field('published_date'),
        )

        original_on_server = original_collection.create()

        created_at = original_on_server.get('created_at')
        original_on_server.pop('created_at')

        self.assertEqual(
            original_on_server,
            {
                'default_sorting_field': 'published_date',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )
        self.typesense_client.collections['book'].documents.create(
            {
                'title': 'The Great Gatsby',
                'published_date': 1925,
            },
        )

        updated_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            skip_index_fields={Book._meta.get_field('published_date')},
        )

        updated_collection.update()
        updated_on_server = self.typesense_client.collections['book'].retrieve()

        self.assertEqual(
            updated_on_server,
            {
                'created_at': created_at,
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': False,
                        'index': False,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 1,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['book'].delete()

    def test_update_schema_facets(self) -> None:
        """Test Schema Update."""
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            default_sorting_field=Book._meta.get_field('published_date'),
        )

        original_on_server = original_collection.create()

        created_at = original_on_server.get('created_at')
        original_on_server.pop('created_at')

        self.assertEqual(
            original_on_server,
            {
                'default_sorting_field': 'published_date',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': False,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': False,
                        'sort': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )
        self.typesense_client.collections['book'].documents.create(
            {
                'title': 'The Great Gatsby',
                'published_date': 1925,
            },
        )

        updated_collection = TypesenseCollection(
            client=self.typesense_client,
            model=Book,
            facets=True,
        )

        updated_collection.update()
        updated_on_server = self.typesense_client.collections['book'].retrieve()

        self.assertEqual(
            updated_on_server,
            {
                'created_at': created_at,
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'facet': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'title',
                        'optional': False,
                        'sort': False,
                        'stem': False,
                        'type': 'string',
                    },
                    {
                        'facet': True,
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'sort': True,
                        'stem': False,
                        'type': 'int64',
                    },
                ],
                'name': 'book',
                'num_documents': 1,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

    def test_update_schema_subsequent_joins(self) -> None:
        """Test Schema Update with a JOIN after initialization."""
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=OptionalFields,
            index_fields={
                OptionalFields._meta.get_field('optional'),
            },
        )

        original_on_server = original_collection.create()

        original_on_server.pop('created_at')

        self.assertEqual(
            original_on_server,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'name': 'optional',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': True,
                    },
                ],
                'name': 'optional_fields',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['optional_fields'].documents.create(
            {
                'optional': 'The Great Gatsby',
            },
        )

        updated_collection = TypesenseCollection(
            client=self.typesense_client,
            model=OptionalFields,
            use_joins=True,
        )
        with self.assertRaises(typesense_exceptions.RequestMalformed):
            updated_collection.update()

        self.typesense_client.collections['optional_fields'].delete()

    def test_update_schema_update_joins(self) -> None:
        """Test Schema Update."""
        original_collection = TypesenseCollection(
            client=self.typesense_client,
            model=OptionalFields,
            parents={
                OptionalFields._meta.get_field('optional_ref'),
            },
            index_fields={
                OptionalFields._meta.get_field('optional'),
            },
            use_joins=True,
        )

        original_on_server = original_collection.create()

        original_on_server.pop('created_at')

        self.assertEqual(
            original_on_server,
            {
                'default_sorting_field': '',
                'enable_nested_fields': False,
                'fields': [
                    {
                        'name': 'optional',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'index': True,
                        'optional': True,
                    },
                    {
                        'name': 'optional_ref_id',
                        'type': 'string',
                        'facet': False,
                        'sort': False,
                        'locale': '',
                        'infix': False,
                        'stem': False,
                        'optional': True,
                        'index': True,
                        'reference': 'reference.id',
                    },
                ],
                'name': 'optional_fields',
                'num_documents': 0,
                'symbols_to_index': [],
                'token_separators': [],
            },
        )

        self.typesense_client.collections['optional_fields'].documents.create(
            {
                'optional': 'The Great Gatsby',
            },
        )

        updated_collection = TypesenseCollection(
            client=self.typesense_client,
            model=OptionalFields,
            parents={
                OptionalFields._meta.get_field('optional_ref'),
            },
            skip_index_fields={
                OptionalFields._meta.get_field('optional_ref'),
            },
            use_joins=True,
        )

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            updated_collection.update()
