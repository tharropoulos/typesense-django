from django.db import models


class AllModelFields(models.Model):
    auto_field = models.AutoField(primary_key=True)
    big_integer_field = models.BigIntegerField()
    binary_field = models.BinaryField()
    boolean_field = models.BooleanField()
    char_field = models.CharField(max_length=100)
    date_field = models.DateField()
    date_time_field = models.DateTimeField()
    decimal_field = models.DecimalField(max_digits=5, decimal_places=2)
    decimal_field_large_decimals = models.DecimalField(max_digits=19, decimal_places=10)
    decimal_field_large_digits = models.DecimalField(decimal_places=2, max_digits=100)
    duration_field = models.DurationField()
    email_field = models.EmailField()
    file_field = models.FileField()
    file_path_field = models.FilePathField()
    float_field = models.FloatField()
    generic_ip_address_field = models.GenericIPAddressField()
    image_field = models.ImageField()
    integer_field = models.IntegerField()
    json_field = models.JSONField()
    positive_big_integer_field = models.PositiveBigIntegerField()
    positive_integer_field = models.PositiveIntegerField()
    positive_small_integer_field = models.PositiveSmallIntegerField()
    slug_field = models.SlugField()
    small_integer_field = models.SmallIntegerField()
    text_field = models.TextField()
    time_field = models.TimeField()
    url_field = models.URLField()


class BigAutoFieldModel(models.Model):
    big_auto_field = models.BigAutoField(primary_key=True)


class SmallAutoFieldModel(models.Model):
    small_auto_field = models.SmallAutoField(primary_key=True)


class UUIDModel(models.Model):
    uuid_field = models.UUIDField(primary_key=True)
