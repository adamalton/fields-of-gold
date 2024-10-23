# Standard library
from contextlib import contextmanager
import json

# Third Party
from django.core import checks
from django.core.exceptions import ValidationError
from django.db.models import JSONField
import pydantic


class PydanticJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, pydantic.BaseModel):
            return o.model_dump(mode="json")
        return super().default(o)


class TypedJSONField(JSONField):
    """ A JSONField which can have an enforced schema using Pydantic models. """

    default_validators = [

    ]

    def __init__(self, *args, type=None, encoder=PydanticJSONEncoder, **kwargs):
        self.type = type
        super().__init__(*args, **{"encoder": encoder, **kwargs})

    def check(self, **kwargs):
        return [
            *super().check(),
            *self._check_type(),
        ]

    def _check_type(self):
        if not issubclass(self.type, pydantic.BaseModel):
            return [checks.Error(
                f"'type' argument must be a Pydantic model class, not {type(self.type)}.",
                obj=self,
                id="fields_of_gold.E001",
            )]
        return []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["type"] = self.type
        return name, path, args, kwargs

    def to_python(self, value):
        """
        Convert the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Return the converted value. Subclasses should override this.
        """
        # This relies on the top-level JSON object being a dict not a list
        if value is None or isinstance(value, self.type):
            return value

        try:
            return self.type(**value)
        except pydantic.ValidationError as error:
            raise ValidationError(str(error)) from error

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        return self.to_python(value)

    def validate(self, value, model_instance):
        """
        Validate value and raise ValidationError if necessary. Subclasses
        should override this to provide validation logic.
        """
        if isinstance(value, self.type):
            json_value = value.model_dump_json()
            super().validate(json_value, model_instance)
            with convert_validation_error():
                self.type.model_validate(value)
        else:
            super().validate(value, model_instance)
            if value is not None:
                with convert_validation_error():
                    self.type(**value)  # Will raise if data is invalid

    # def pre_save(self, model_instance, add):
    #     """ Enforce validation here??. """
    #     self.validate()
    #     pass

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, self.type):
            value = value.model_dump()
        return super().get_db_prep_value(value, connection, prepared)
        # if isinstance(value, self.type):
        #     return value.model_dump_json()
        # return value

    # We might need to override this
    # def value_to_string(self, obj):
    #     """
    #     Return a string value of this field from the passed obj.
    #     This is used by the serialization framework.
    #     """
    #     return str(self.value_from_object(obj))


@contextmanager
def convert_validation_error():
    try:
        yield
    except pydantic.ValidationError as error:
        raise ValidationError(str(error)) from error
