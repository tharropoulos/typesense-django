# Typesense Django

<p align="center">
<h3 align="center">Automate your <a href="https://github.com/typesense/typesense">Typesense</a> workflow in Django 🚀</h3>
</p>

<p align="center">
<a href="https://github.com/tharropoulos/typesense-django/actions/workflows/tests.yml">
<img src="https://github.com/tharropoulos/typesense-django/actions/workflows/tests.yml/badge.svg"/></a>
<a href="https://github.com/typesense"><img src="https://img.shields.io/github/stars/tharropoulos/typesense-django?label=GitHub%20Stars%20✨&style=flat"></a>
<a href="https://www.codefactor.io/repository/github/tharropoulos/typesense-django/overview/master"><img src="https://www.codefactor.io/repository/github/tharropoulos/typesense-django/badge/master" alt="CodeFactor" /></a>
</p>

<p align="center">
  <a href="https://typesense.org">Website</a> | 
  <a href="https://typesense.org/docs/">Documentation</a> | 
  <a href="#roadmap">Roadmap</a> | 
  <a href="https://join.slack.com/t/typesense-community/shared_invite/zt-2fetvh0pw-ft5y2YQlq4l_bPhhqpjXig">Slack Community</a> | 
  <a href="https://threads.typesense.org/kb">Community Threads</a> | 
  <a href="https://twitter.com/typesense">Twitter</a>
</p>
<br>

Typesense Django is a powerful integration package that automates the creation and management of Typesense collections for Django models. It seamlessly bridges the gap between Django's ORM and Typesense's search capabilities.

## Features

- **Automated Collection Generation**: Create or update Typesense collections based on your Django models.
- **Flexible Field Mapping**: Customize how Django model fields are mapped to Typesense schema fields.
- **Relation Handling**: Support for parent-child relationships and joins.
- **Geopoint Support**: Easily index and search geospatial data.
- **Faceting and Sorting**: Configure facet and sorting fields with ease.
- **Detailed Control**: Fine-tune indexing, faceting, and sorting on a per-field basis.
- **Type Safety**: Fully typed implementation for reliable development.

## Roadmap

- [ ] Locale Support
- [ ] Infix Support
- [ ] Stemming Support
- [ ] Image Search Support
- [ ] Automatic Indexing
- [ ] Full Re-indexing

## Installation

1. Ensure you have Django and Typesense installed in your project:

   ```
   pip install django typesense
   ```

2. Install the Typesense Django package:

   ```
   pip install typesense-django
   ```

3. Add `'typesense_integration'` to your `INSTALLED_APPS` in `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...
       'typesense_integration',
       ...
   ]
   ```

## Usage

1. Import the necessary classes:

   ```python
   from typesense import Client
   from typesense_integration.models import TypesenseCollection
   ```

2. Create a Typesense client:

   ```python
   client = Client({
       'nodes': [{'host': 'localhost', 'port': '8108', 'protocol': 'http'}],
       'api_key': 'your_api_key',
       'connection_timeout_seconds': 2
   })
   ```

3. Define your Django model:

   ```python
   from django.db import models

   class Book(models.Model):
       title = models.CharField(max_length=100)
       author = models.CharField(max_length=100)
       publication_year = models.IntegerField()
   ```

4. Create a Typesense collection for your model:

   ```python
   ts_collection = TypesenseCollection(
       client=client,
       model=Book,
       index_fields={'title', 'author', 'publication_year'},
       facets={'author'},
       sorting_fields={'publication_year'}
   )

   ts_collection.create()
   ```

5. To update the collection schema:

   ```python
   ts_collection.update()
   ```

## Configuration

You can configure the Typesense connection in your Django `settings.py`:

```python
TYPESENSE_HOST = 'localhost'
TYPESENSE_PORT = 8108
TYPESENSE_PROTOCOL = 'http'
TYPESENSE_API_KEY = 'your_api_key'
```

## Advanced Usage

### Geopoint Indexing

```python
class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

ts_collection = TypesenseCollection(
    client=client,
    model=Location,
    index_fields={'name'},
    geopoints={('latitude', 'longitude')}
)
```

### Relation Handling

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

ts_collection = TypesenseCollection(
    client=client,
    model=Book,
    index_fields={'title'},
    parents={'author'},
    use_joins=True
)
```

## Testing

To run the tests, use the following command:

```
python manage.py test
```
