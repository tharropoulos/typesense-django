from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import (
    Author,
    Book,
    Chapter,
    ManyToManyLeftImplicit,
    ManyToManyLinkExplicit,
    Reader,
    VerboseRelation,
)
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class RelationTests(TypesenseCollectionTestCase):
    """Tests for relations."""

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
                    'optional': False,
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
        self.assertEqual(collection.typesense_relations, [])

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
