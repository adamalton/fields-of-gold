# Third Party
from django.core.exceptions import ValidationError
from django.db import models
import pydantic

# Fields of gold
from fields_of_gold import TypedJSONField
from .base import ExtraModelsTestCase


class SimpleType(pydantic.BaseModel):
    my_int: int
    my_str: str
    optional_int: int = 1
    optional_str: str = "String"


class SimpleTypedJSONModel(models.Model):

    class Meta:
        app_label = "fields_of_gold"

    typed_field = TypedJSONField(type=SimpleType)


class TypedJSONFieldTestCase(ExtraModelsTestCase):
    """ Tests for the TypedJSONField. """

    test_models = [SimpleTypedJSONModel]

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

    def test_non_nullable_field_raises_validation_error(self):
        instance = SimpleTypedJSONModel()
        self.assertRaisesRegex(
            ValidationError, r"typed_field.+cannot be null", instance.full_clean
        )
        instance.typed_field = SimpleType(my_int=1, my_str="cake")
        instance.full_clean()
