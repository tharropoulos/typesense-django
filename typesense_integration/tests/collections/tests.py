from __future__ import annotations

from unittest import mock

from django.test import TestCase
from typesense import Client


class TypesenseCollectionTestCase(TestCase):
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
        """Initialize the collection with a fresh mock client."""
        return mock.create_autospec(Client)
