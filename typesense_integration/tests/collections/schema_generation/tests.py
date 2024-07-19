from __future__ import annotations

from django.conf import settings
from django.test import TestCase
from typesense import Client

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import (
    Book,
    GeoPoint,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
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
                        'name': 'title',
                        'type': 'string',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'id',
                        'type': 'string',
                        'facet': False,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': False,
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
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'sort': True,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author',
                        'type': 'object',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'chapter',
                        'type': 'object[]',
                        'facet': False,
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
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'sort': True,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'email',
                        'type': 'string',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'birth_date',
                        'type': 'int64',
                        'facet': False,
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
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'birth_date',
                        'optional': False,
                        'sort': True,
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
                        'index': True,
                        'optional': False,
                        'reference': 'custom_name.id',
                    },
                    {
                        'name': 'custom_name',
                        'type': 'object',
                        'facet': False,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': True,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': True,
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
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'sort': True,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': True,
                        'index': True,
                        'optional': False,
                        'reference': 'author.id',
                    },
                    {
                        'name': 'author',
                        'type': 'object',
                        'facet': False,
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
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'sort': True,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'index': False,
                        'optional': False,
                    },
                    {
                        'name': 'author_id',
                        'type': 'string',
                        'facet': False,
                        'index': False,
                        'optional': False,
                        'reference': 'author.id',
                    },
                    {
                        'name': 'author',
                        'type': 'object',
                        'facet': False,
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
                        'index': False,
                        'infix': False,
                        'locale': '',
                        'name': 'published_date',
                        'optional': False,
                        'sort': True,
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
            skip_index_fields={
                Book._meta.get_field('published_date'),
            },
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'published_date',
                        'type': 'int64',
                        'facet': False,
                        'index': False,
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
                        'index': False,
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
                        'index': True,
                        'optional': False,
                    },
                    {
                        'name': 'lat_long',
                        'type': 'geopoint',
                        'facet': False,
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
                        'index': True,
                        'infix': False,
                        'locale': '',
                        'optional': False,
                        'sort': True,
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
