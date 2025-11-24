# Standard library
import datetime as dt

# Third Party
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.test import TestCase, TransactionTestCase
import pydantic

# Fields of gold
from fields_of_gold import TypedJSONField
from .base import ExtraModelsMixin


class SimpleType(pydantic.BaseModel):
    my_int: int
    my_str: str
    optional_int: int = 1
    optional_str: str = "String"


class SimpleTypedJSONModel(models.Model):
    class Meta:
        app_label = "fields_of_gold"

    typed_field = TypedJSONField(type=SimpleType)


class TypeWithDateTimes(pydantic.BaseModel):
    datetime_field: dt.datetime


class ModelWithDateTime(models.Model):
    class Meta:
        app_label = "fields_of_gold"

    typed_field = TypedJSONField(type=TypeWithDateTimes)


class StrictModelWithDateTime(models.Model):
    class Meta:
        app_label = "fields_of_gold"

    typed_field = TypedJSONField(type=TypeWithDateTimes, force_valid=True)


class TypedJSONFieldTestCase(ExtraModelsMixin, TestCase):
    """Tests for the TypedJSONField."""

    test_models = [SimpleTypedJSONModel, ModelWithDateTime]

    def test_basic_usage(self):
        instance = SimpleTypedJSONModel()
        instance.typed_field = SimpleType(my_int=1, my_str="cake")
        instance.typed_field.my_str = "not cake"
        instance.save()
        # To a full re-fetch so that we're testing a complete new instantiation from the DB
        instance = SimpleTypedJSONModel.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.typed_field, SimpleType)
        self.assertEqual(instance.typed_field.my_int, 1)
        self.assertEqual(instance.typed_field.my_str, "not cake")

    def test_data_set_as_dict_is_converted(self):
        """If the field's attribute value is set as a python dict, it should be converted to the
        Pydantic model type.
        """
        instance = SimpleTypedJSONModel()
        instance.typed_field = {"my_int": 1, "my_str": "hello"}
        instance.save()
        # As is the case with other Django fields (e.g. BooleanField), setting a value which is
        # valid but which is not the same type (e.g. setting 1 instead of True) will not get coerced
        # to the correct type simply by saving. It only gets coerced when fetching from the DB.
        instance.refresh_from_db()
        self.assertIsInstance(instance.typed_field, SimpleType)

    def test_invalid_data_raises_validation_error(self):
        """Calling full_clean with invalid data should raise a Django ValidationError."""
        instance = SimpleTypedJSONModel()
        instance.typed_field = {"my_int": "Cannot be an int", "my_str": "whatever"}
        self.assertRaisesRegex(ValidationError, r"typed_field.+my_int", instance.full_clean)

    def test_non_nullable_field_raises_validation_error(self):
        instance = SimpleTypedJSONModel()
        self.assertRaisesRegex(ValidationError, r"typed_field.+cannot be null", instance.full_clean)
        instance.typed_field = SimpleType(my_int=1, my_str="cake")
        instance.full_clean()

    def test_modifying_and_resaving(self):
        """Regression test for an issue where modifying a field in the object and resaving would
        cause a a JSON encoding error.
        """
        instance = ModelWithDateTime(typed_field=TypeWithDateTimes(datetime_field=dt.datetime.now()))
        instance.save()
        instance.refresh_from_db()
        self.assertIsInstance(instance.typed_field, TypeWithDateTimes)
        self.assertIsInstance(instance.typed_field.datetime_field, dt.datetime)
        instance.typed_field.datetime_field = dt.datetime.now()
        instance.save()
        instance.refresh_from_db()
        self.assertIsInstance(instance.typed_field, TypeWithDateTimes)
        self.assertIsInstance(instance.typed_field.datetime_field, dt.datetime)


# Separate test case for things which raise IntegrityError, as it screws the normal transaction-based test stuff
class ForceValidTestCase(ExtraModelsMixin, TransactionTestCase):
    test_models = [ModelWithDateTime, StrictModelWithDateTime]

    def test_force_valid(self):
        """Test the behaviour of the `force_valid` kwarg."""
        instance = ModelWithDateTime(typed_field=TypeWithDateTimes(datetime_field=dt.datetime.now()))
        # We have to modify the value afterwards to circumvent the Pydantic construction-time validation
        instance.typed_field.datetime_field = None
        # Without the `force_valid` kwarg, the save should be allowed
        instance.save()
        instance = StrictModelWithDateTime(typed_field=TypeWithDateTimes(datetime_field=dt.datetime.now()))
        # We have to modify the value afterwards to circumvent the Pydantic construction-time validation
        instance.typed_field.datetime_field = None
        self.assertRaises(IntegrityError, instance.save)
        # If we now populate the value, it should be save-able
        instance.typed_field.datetime_field = dt.datetime.now()
        instance.save()
        instance.refresh_from_db()
        self.assertIsInstance(instance.typed_field, TypeWithDateTimes)
        self.assertIsInstance(instance.typed_field.datetime_field, dt.datetime)
