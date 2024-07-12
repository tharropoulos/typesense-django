from __future__ import annotations

from unittest import mock

from django.test import TestCase
from typesense import Client
from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import (
    Author,
    Book,
    Chapter,
    CompositeForeignKey,
    GeoPoint,
    InvalidField,
    JoinOnAnotherField,
    ManyToManyLeftImplicit,
    ManyToManyLinkExplicit,
    Reader,
    Wrong,
)


class TypesenseCollectionTests(TestCase):
    """Tests for the TypesenseCollection class."""

    def setUp(self):
        """Set up the test environment."""
        self.mock_client_constructor = mock.patch(
            'typesense.Client',
        ).start()
        self.addCleanup(
            mock.patch.stopall,
        )  # Ensure all patches are stopped after each test

    def mock_client(self) -> Client:
        """Helper method to initialize the collection with a fresh mock client."""
        return mock.create_autospec(Client)

    def test_missing_args(self):
        """Test that it raises an exception when missing required args."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(TypeError):
            TypesenseCollection(client=mock_client_instance)

        with self.assertRaises(TypeError):
            TypesenseCollection(model=Author)

    def test_malformed_args(self):
        """Test that it raises an exception when args are malformed."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(client=mock_client_instance, model=Wrong)

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(client=Wrong, model=Author)

    def test_one_to_many_relation(self):
        """Test one-to-many relation. The author has many books."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(model=Author, client=mock_client_instance)

        self.assertEqual(collection.name, 'author')
        self.assertEqual(collection.children, {Author._meta.get_field('book')})
        self.assertEqual(collection.parents, set())

    def test_no_relations(self):
        """Test no relations."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(client=mock_client_instance, model=Reader)
        self.assertEqual(collection.name, 'reader')
        self.assertEqual(
            collection.index_fields,
            {
                Reader._meta.get_field('name'),
                Reader._meta.get_field('email'),
                Reader._meta.get_field('birth_date'),
            },
        )
        self.assertEqual(collection.children, set())
        self.assertEqual(collection.parents, set())

    def test_implicit_many_to_many(self):
        """Test implicit many-to-many relation. If there's no link model it should raise."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=ManyToManyLeftImplicit,
            )

    def test_explicit_many_to_many(self):
        """Test explicit many-to-many relation. An intermediary collection should be used."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=ManyToManyLinkExplicit,
        )
        self.assertEqual(collection.name, 'manytomanylinkexplicit')
        self.assertEqual(
            collection.index_fields,
            set(),
        )
        self.assertEqual(collection.children, set())
        self.assertEqual(
            collection.parents,
            {
                ManyToManyLinkExplicit._meta.get_field('left'),
                ManyToManyLinkExplicit._meta.get_field('right'),
            },
        )

    def test_many_to_one(self):
        """Test many-to-one relation. The chapter has one book."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Chapter,
        )
        self.assertEqual(collection.name, 'chapter')
        self.assertEqual(collection.parents, {Chapter._meta.get_field('book')})

    def test_both_relations(self):
        """Test both relations. Book has many chapter and only one author."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
        )
        self.assertEqual(collection.name, 'book')
        self.assertEqual(collection.parents, {Book._meta.get_field('author')})
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )

    def test_override_id_field(self):
        """Test that it can override the default id field."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            override_id=True,
        )
        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('id'),
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(collection.parents, {Book._meta.get_field('author')})
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )

    def test_explicit_index_fields(self):
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

    def test_explicit_parents(self):
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

    def test_explicit_children(self):
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

    def test_joins(self):
        """Test that it can handle multiple joins."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            index_fields={
                Book._meta.get_field('title'),
            },
            parents={Book._meta.get_field('author')},
            children={Book._meta.get_field('chapter')},
            use_joins=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
            },
        )
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'author_id',
                    'reference': 'author.id',
                    'type': 'string',
                },
            ],
        )

    def test_joins_other_than_id(self):
        """Test that it can handle joins on fields other than id."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=JoinOnAnotherField,
            use_joins=True,
        )

        self.assertEqual(collection.name, 'joinonanotherfield')
        self.assertEqual(
            collection.index_fields,
            set(),
        )
        self.assertEqual(
            collection.parents,
            {
                JoinOnAnotherField._meta.get_field('reference'),
            },
        )

        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'reference_number',
                    'reference': 'reference.number',
                    'type': 'int32',
                },
            ],
        )

    def test_joins_composite_key(self):
        """Test that it can handle composite keys in joins."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=CompositeForeignKey,
                parents={CompositeForeignKey._meta.get_field('reference')},
                use_joins=True,
            )

    def test_warn_foreign_field(self):
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

    def test_reference_in_index_fields(self):
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

    def test_wrong_reference(self):
        """Test that it raises if a reference is not in the model's foreign key fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('author'),
                },
                parents={Author._meta.get_field('name')},
            )

    def test_wrong_referenced_by(self):
        """Test that it raises if a referenced_by is not in another model's foreign keys."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('author'),
                },
                children={Author._meta.get_field('name')},
            )

    def test_ignore_duplicate_names(self):
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

    def test_raise_duplicate_names(self):
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

    def test_invalid_model_attribute_type(self):
        """Test that it raises if a model attribute is not a field."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=InvalidField,
            )

    def test_valid_attribute_in_model_with_invalid(self):
        """Test that it doesn't raise if the attributes passed are valid."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=InvalidField,
            index_fields={
                InvalidField._meta.get_field('valid_type'),
            },
        )

        self.assertEqual(collection.name, 'invalidfield')
        self.assertEqual(
            collection.index_fields,
            {InvalidField._meta.get_field('valid_type')},
        )

    def test_all_detail_relations(self):
        """Test that it can handle all relations with detailed relations."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            detailed_parents=True,
            detailed_children=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'author',
                    'type': 'object',
                },
                {
                    'name': 'chapter',
                    'type': 'object[]',
                },
            ],
        )

    def test_detailed_relations_with_joins(self):
        """Test that it can handle all relations with detailed references and joins."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            detailed_parents=True,
            detailed_children=True,
            use_joins=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {'name': 'author_id', 'type': 'string', 'reference': 'author.id'},
                {'name': 'author', 'type': 'object'},
                {'name': 'chapter', 'type': 'object[]'},
            ],
        )

    def test_some_detail_relations(self):
        """Test that it can handle some relations with detailed references."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            detailed_parents={
                Book._meta.get_field('author'),
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
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'author',
                    'type': 'object',
                },
            ],
        )

    def test_raises_detail_relation_not_a_subset(self):
        """Test that it raises if detailed relation is not a subset of relations."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                detailed_parents={
                    Book._meta.get_field('chapter'),
                },
            )

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                detailed_children={
                    Book._meta.get_field('author'),
                },
            )

    def test_all_facets(self):
        """Test that it can handle all facets."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            facets=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(
            collection.facets,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'title',
                    'type': 'string',
                    'facet': True,
                },
                {
                    'name': 'published_date',
                    'type': 'int64',
                    'facet': True,
                },
            ],
        )

    def test_some_facets(self):
        """Test that it can handle some facets."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            facets={
                Book._meta.get_field('title'),
            },
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.facets,
            {
                Book._meta.get_field('title'),
            },
        )
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'title',
                    'type': 'string',
                    'facet': True,
                },
                {
                    'name': 'published_date',
                    'type': 'int64',
                },
            ],
        )

    def test_facets_with_joins(self):
        """Test that it can handle all facets with joins."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            use_joins=True,
            facets=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )
        self.assertEqual(
            collection.facets,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'author_id',
                    'type': 'string',
                    'reference': 'author.id',
                    'facet': True,
                },
            ],
        )

    def test_warns_facets_on_relation_with_no_joins(self):
        """Test that it warns if a facet field is a relation but there's no join."""
        mock_client_instance = self.mock_client()

        with self.assertWarns(UserWarning):
            collection = TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('title'),
                },
                parents={Book._meta.get_field('author')},
                facets={Book._meta.get_field('author'), Book._meta.get_field('title')},
            )

            self.assertEqual(collection.name, 'book')
            self.assertEqual(
                collection.parents,
                {
                    Book._meta.get_field('author'),
                },
            )
            self.assertEqual(
                collection.facets,
                {
                    Book._meta.get_field('author'),
                    Book._meta.get_field('title'),
                },
            )
            self.assertEqual(collection.typesense_relations, [])

    def test_raises_facets_not_a_subset(self):
        """Test that it raises if a facet is not a subset of `index_fields` or relations."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('title'),
                },
                facets={
                    Book._meta.get_field('author'),
                },
            )

    def test_geopoint_in_index_fields(self):
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

    def test_geopoints(self):
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

        self.assertEqual(collection.name, 'geopoint')
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

    def test_geopoints_not_float(self):
        """Test that it raises if a geopoint is not a float."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=GeoPoint,
                geopoints={
                    (GeoPoint._meta.get_field('lat'), GeoPoint._meta.get_field('name')),
                },
            )

    def test_geopoints_not_tuple(self):
        """Test that it raises if a geopoint is not a tuple."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(TypeError):
            TypesenseCollection(
                client=mock_client_instance,
                model=GeoPoint,
                geopoints={
                    GeoPoint._meta.get_field('lat'),
                },
            )
