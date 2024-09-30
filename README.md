Fields of Gold
==============

A Django library providing useful DB model fields.


Installation & setup
--------------------

1. `pip install fields-of-gold`
2. Add `"fields_of_gold"` to your `INSTALLED_APPS`.
3. Use the fields in your models.


Fields
------

### TypedJSONField

A JSONField which can have an enforced schema using [Pydantic](https://docs.pydantic.dev/) models.
The underlying storage uses the JSONField, but you can interact with the data via the declared Pydantic type.

Because the underlying storage is using JSON, you can swap out existing JSONFields for TypedJSONField without
having to perform any manipulation to the stored data, so long as the existing data conforms to your Pydantic schema.

Example usage:

```python
from django.db import models
from fields_of_gold import TypedJSONField
from pydantic import BaseModel

class MyType(BaseModel):
    my_int: int
    my_str: str


class MyModel(models.Model):
    typed_field = TypedJSONField(type=MyType)


...

instance = MyModel(typed_field=MyType(my_int=1, my_str=2))
instance.full_clean()
instance.save()
```


### NullableOneToOneField

A modified OneToOneField which is unique but nullable.

In Django, using `ForeignKey(unique=True, null=True)` will raise a warning recommending that you should use
`OneToOneField` instead. But using `OneToOneField(null=True)` won't respect the null-able-ness, so trying to
access `obj.my_one_to_one_field` will raise `DoesNotExist`, and the same with the reverse lookup.

This field solves that problem by allowing the field to be nullable while still enforcing its uniqueness and
not giving you unnecessary warnings.
