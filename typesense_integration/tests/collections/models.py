from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    birth_date = models.DateField()


class Book(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateField()


class Chapter(models.Model):
    title = models.CharField(max_length=100)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    chapter_content = models.TextField()


class Reader(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    birth_date = models.DateField()


class CompositeReference(models.Model):
    first = models.IntegerField(unique=True)
    second = models.CharField(max_length=100, unique=True)


class CompositeForeignKey(models.Model):
    first = models.IntegerField()
    second = models.CharField(max_length=100)
    reference = models.ForeignObject(
        CompositeReference,
        to_fields=['first', 'second'],
        on_delete=models.CASCADE,
        from_fields=['first', 'second'],
    )


class Reference(models.Model):
    number = models.IntegerField(unique=True)


class JoinOnAnotherField(models.Model):
    reference = models.ForeignKey(
        Reference,
        to_field='number',
        on_delete=models.CASCADE,
    )


class InvalidField(models.Model):
    valid_type = models.CharField(max_length=100)
    invalid_type = models.BinaryField()


class ManyToManyLeftImplicit(models.Model):
    name = models.CharField(max_length=100)


class ManyToManyLeftExplicit(models.Model):
    name = models.CharField(max_length=100)


class ManyToManyRightExplicit(models.Model):
    name = models.CharField(max_length=100)


class ManyToManyLinkExplicit(models.Model):
    left = models.ForeignKey(ManyToManyLeftExplicit, on_delete=models.CASCADE)
    right = models.ForeignKey(ManyToManyRightExplicit, on_delete=models.CASCADE)


class ManyToManyRightImplicit(models.Model):
    name = models.CharField(max_length=100)
    lefts = models.ManyToManyField(ManyToManyLeftImplicit, related_name='rights')


class Wrong:
    def __init__(self) -> None:
        """This is not a model class."""
        pass


class GeoPoint(models.Model):
    lat = models.FloatField()
    long = models.DecimalField(max_digits=9, decimal_places=6)
    name = models.CharField(max_length=100)


class VerboseName(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Custom Name'


class VerboseRelation(models.Model):
    custom_name = models.ForeignKey(
        VerboseName,
        on_delete=models.CASCADE,
    )


class OptionalFields(models.Model):
    optional = models.CharField(max_length=100, null=True)
    optional_lat = models.FloatField(null=True)
    optional_long = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    optional_ref = models.ForeignKey(Reference, on_delete=models.CASCADE, null=True)
    required_lat = models.FloatField()


class MultipleSortableFields(models.Model):
    first = models.IntegerField()
    second = models.DateField()
    name = models.CharField(max_length=100)
