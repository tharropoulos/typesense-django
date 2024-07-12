from __future__ import annotations

from unittest import mock
from uuid import UUID

from django.test import TestCase
from typesense import Client
from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.schema_validation.models import (
    AllModelFields,
    BigAutoFieldModel,
    SmallAutoFieldModel,
    UUIDModel,
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

    def test_auto_field(self):
        """Test AutoField validation."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('auto_field'),
            },
        )

        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'auto_field',
                    'type': 'int32',
                },
            ],
        )

    def test_big_integer_field(self):
        """Test BigIntegerField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('big_integer_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'big_integer_field',
                    'type': 'int64',
                },
            ],
        )

    def test_binary_field(self):
        """Test BinaryField validation."""
        mock_client_instance = self.mock_client()
        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                model=AllModelFields,
                client=mock_client_instance,
                index_fields={
                    AllModelFields._meta.get_field('binary_field'),
                },
            )

    def test_boolean_field(self):
        """Test BooleanField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('boolean_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'boolean_field',
                    'type': 'bool',
                },
            ],
        )

    def test_char_field(self):
        """Test CharField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('char_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'char_field',
                    'type': 'string',
                },
            ],
        )

    def test_date_field(self):
        """Test DateField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('date_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'date_field',
                    'type': 'int64',
                },
            ],
        )

    def test_date_time_field(self):
        """Test DateTimeField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('date_time_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'date_time_field',
                    'type': 'int64',
                },
            ],
        )

    def test_decimal_field(self):
        """Test DecimalField validation that's mapped to float32."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('decimal_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'decimal_field',
                    'type': 'float32',
                },
            ],
        )

    def test_decimal_field_large_decimal_points(self):
        """Test DecimalField validation that's mapped to float64 because of decimal points."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('decimal_field_large_decimals'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'decimal_field_large_decimals',
                    'type': 'float64',
                },
            ],
        )

    def test_decimal_field_large_digits(self):
        """Test DecimalField validation that's mapped to float64 because of total digits."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('decimal_field_large_digits'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'decimal_field_large_digits',
                    'type': 'float64',
                },
            ],
        )

    def test_duration_field(self):
        """Test DurationField validation."""
        mock_client_instance = self.mock_client()
        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                model=AllModelFields,
                client=mock_client_instance,
                index_fields={
                    AllModelFields._meta.get_field('duration_field'),
                },
            )

    def test_email_field(self):
        """Test EmailField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('email_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'email_field',
                    'type': 'string',
                },
            ],
        )

    def test_file_field(self):
        """Test FileField validation."""
        mock_client_instance = self.mock_client()
        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                model=AllModelFields,
                client=mock_client_instance,
                index_fields={
                    AllModelFields._meta.get_field('file_field'),
                },
            )

    def test_file_path_field(self):
        """Test FilePathField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('file_path_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'file_path_field',
                    'type': 'string',
                },
            ],
        )

    def test_float_field(self):
        """Test FloatField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('float_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'float_field',
                    'type': 'float32',
                },
            ],
        )

    def test_generic_ip_address_field(self):
        """Test GenericIpAddressField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('generic_ip_address_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'generic_ip_address_field',
                    'type': 'string',
                },
            ],
        )

    def test_image_field(self):
        """Test ImageField validation."""
        mock_client_instance = self.mock_client()
        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                model=AllModelFields,
                client=mock_client_instance,
                index_fields={
                    AllModelFields._meta.get_field('image_field'),
                },
            )

    def test_integer_field(self):
        """Test IntegerField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('integer_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'integer_field',
                    'type': 'int32',
                },
            ],
        )

    def test_json_field(self):
        """Test JsonField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('json_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'json_field',
                    'type': 'string',
                },
            ],
        )

    def test_positive_big_integer_field(self):
        """Test PositiveBigIntegerField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('positive_big_integer_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'positive_big_integer_field',
                    'type': 'int64',
                },
            ],
        )

    def test_positive_integer_field(self):
        """Test PositiveIntegerField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('positive_integer_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'positive_integer_field',
                    'type': 'int32',
                },
            ],
        )

    def test_positive_small_integer_field(self):
        """Test PositiveSmallIntegerField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('positive_small_integer_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'positive_small_integer_field',
                    'type': 'int32',
                },
            ],
        )

    def test_slug_field(self):
        """Test SlugField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('slug_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'slug_field',
                    'type': 'string',
                },
            ],
        )

    def test_small_integer_field(self):
        """Test SmallIntegerField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('small_integer_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'small_integer_field',
                    'type': 'int32',
                },
            ],
        )

    def test_text_field(self):
        """Test TextField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('text_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'text_field',
                    'type': 'string',
                },
            ],
        )

    def test_time_field(self):
        """Test TimeField validation."""
        mock_client_instance = self.mock_client()
        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                model=AllModelFields,
                client=mock_client_instance,
                index_fields={
                    AllModelFields._meta.get_field('time_field'),
                },
            )

    def test_url_field(self):
        """Test UrlField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                AllModelFields._meta.get_field('url_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'url_field',
                    'type': 'string',
                },
            ],
        )

    def test_big_auto_field(self):
        """Test BigAutoField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                BigAutoFieldModel._meta.get_field('big_auto_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'big_auto_field',
                    'type': 'int64',
                },
            ],
        )

    def test_small_auto_field(self):
        """Test SmallAutoField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                SmallAutoFieldModel._meta.get_field('small_auto_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'small_auto_field',
                    'type': 'int32',
                },
            ],
        )

    def test_uuid_field(self):
        """Test UUIDField validation."""
        mock_client_instance = self.mock_client()
        collection = TypesenseCollection(
            model=AllModelFields,
            client=mock_client_instance,
            index_fields={
                UUIDModel._meta.get_field('uuid_field'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'uuid_field',
                    'type': 'string',
                },
            ],
        )
