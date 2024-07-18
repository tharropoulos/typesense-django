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
    Reference,
    VerboseName,
    VerboseRelation,
    Wrong,
)


class TypesenseCollectionTests(TestCase):
    """Tests for the TypesenseCollection class."""

    def setUp(self) -> None:
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

    def test_missing_args(self) -> None:
        """Test that it raises an exception when missing required args."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(KeyError):
            TypesenseCollection(client=mock_client_instance)  # type: ignore[call-arg]

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(model=Author)  # type: ignore[call-arg]

    def test_malformed_args(self) -> None:
        """Test that it raises an exception when args are malformed."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(client=mock_client_instance, model=Wrong)  # type: ignore[arg-type]

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(client=Wrong, model=Author)

    def test_verbose_model_name(self) -> None:
        """Test that it can handle verbose model names."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=VerboseName,
        )

        self.assertEqual(collection.name, 'custom_name')

    def test_default_sorting_field(self) -> None:
        """Test that it can handle default sorting fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Reference,
            default_sorting_field=Reference._meta.get_field('number'),
        )

        self.assertEqual(
            collection.default_sorting_field,
            Reference._meta.get_field('number'),
        )

    def test_raises_default_sorting_field_not_number(self) -> None:
        """Test that it raises if default sorting field is not a number."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                default_sorting_field=Book._meta.get_field('title'),  # type: ignore[arg-type]
            )

    def test_raises_default_sorting_field_not_in_index_fields(self) -> None:
        """Test that it raises if default sorting field is not in indexed fields."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Reference,
                skip_index_fields={Reference._meta.get_field('number')},
                default_sorting_field=Reference._meta.get_field('number'),
            )

    def test_raises_default_sorting_field_not_in_model(self) -> None:
        """Test that it raises if default sorting field is not in model."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                default_sorting_field=Reference._meta.get_field('number'),
            )

    def test_warns_default_sorting_field_not_in_model(self) -> None:
        """Test that it warns if a default sorting field is not in the model, but is indexed."""
        mock_client_instance = self.mock_client()

        with self.assertWarns(UserWarning):
            collection = TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={Reference._meta.get_field('number')},
                default_sorting_field=Reference._meta.get_field('number'),
            )

            self.assertEqual(
                collection.default_sorting_field,
                Reference._meta.get_field('number'),
            )

    def test_verbose_relations(self) -> None:
        """Test that it can handle verbose relations."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=VerboseRelation,
            use_joins=True,
        )

        self.assertEqual(
            collection.parents,
            {
                VerboseRelation._meta.get_field('custom_name'),
            },
        )

        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'custom_name_id',
                    'reference': 'custom_name.id',
                    'type': 'string',
                    'facet': False,
                    'index': True,
                },
            ],
        )

    def test_one_to_many_relation(self) -> None:
        """Test one-to-many relation. The author has many books."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(model=Author, client=mock_client_instance)

        self.assertEqual(collection.name, 'author')
        self.assertEqual(collection.children, {Author._meta.get_field('book')})
        self.assertEqual(collection.parents, set())

    def test_no_relations(self) -> None:
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

    def test_implicit_many_to_many(self) -> None:
        """Test implicit many-to-many relation. If there's no link model it should raise."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=ManyToManyLeftImplicit,
            )

    def test_explicit_many_to_many(self) -> None:
        """Test explicit many-to-many relation. An intermediary collection should be used."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=ManyToManyLinkExplicit,
        )
        self.assertEqual(collection.name, 'many_to_many_link_explicit')
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

    def test_many_to_one(self) -> None:
        """Test many-to-one relation. The chapter has one book."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Chapter,
        )
        self.assertEqual(collection.name, 'chapter')
        self.assertEqual(collection.parents, {Chapter._meta.get_field('book')})

    def test_both_relations(self) -> None:
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


    def test_override_id_field(self) -> None:
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

    def test_joins(self) -> None:
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
                    'facet': False,
                    'index': True,
                },
            ],
        )

    def test_joins_other_than_id(self) -> None:
        """Test that it can handle joins on fields other than id."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=JoinOnAnotherField,
            use_joins=True,
        )

        self.assertEqual(collection.name, 'join_on_another_field')
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
                    'facet': False,
                    'index': True,
                    'name': 'reference_number',
                    'reference': 'reference.number',
                    'type': 'int32',
                },
            ],
        )

    def test_joins_composite_key(self) -> None:
        """Test that it can handle composite keys in joins."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=CompositeForeignKey,
                parents={CompositeForeignKey._meta.get_field('reference')},  # type: ignore[arg-type]
                use_joins=True,
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

    def test_all_detail_relations(self) -> None:
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
                    'index': True,
                    'facet': False,
                },
                {
                    'name': 'chapter',
                    'type': 'object[]',
                    'index': True,
                    'facet': False,
                },
            ],
        )

    def test_detailed_relations_with_joins(self) -> None:
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
                {
                    'name': 'author_id',
                    'type': 'string',
                    'reference': 'author.id',
                    'index': True,
                    'facet': False,
                },
                {'name': 'author', 'type': 'object', 'index': True, 'facet': False},
                {
                    'name': 'chapter',
                    'type': 'object[]',
                    'index': True,
                    'facet': False,
                },
            ],
        )

    def test_some_detail_relations(self) -> None:
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
                    'index': True,
                    'facet': False,
                },
            ],
        )

    def test_raises_detail_relation_not_a_subset(self) -> None:
        """Test that it raises if detailed relation is not a subset of relations."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                detailed_parents={
                    Book._meta.get_field('chapter'),  # type: ignore[arg-type]
                },
            )

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                detailed_children={
                    Book._meta.get_field('author'),  # type: ignore[arg-type]
                },
            )

    def test_all_facets(self) -> None:
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
                    'index': True,
                },
                {
                    'name': 'published_date',
                    'type': 'int64',
                    'facet': True,
                    'index': True,
                },
            ],
        )

    def test_some_facets(self) -> None:
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
                    'index': True,
                },
                {
                    'name': 'published_date',
                    'type': 'int64',
                    'facet': False,
                    'index': True,
                },
            ],
        )

    def test_facets_with_joins(self) -> None:
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
                    'index': True,
                },
            ],
        )

    def test_warns_facets_on_relation_with_no_joins(self) -> None:
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

    def test_raises_facets_not_a_subset(self) -> None:
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
