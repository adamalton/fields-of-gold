from django.db.models import OneToOneField
from django.db.models.fields.related_descriptors import (
    ForwardOneToOneDescriptor,
    ReverseOneToOneDescriptor,
)


class NullableForwardOneToOneDescriptor(ForwardOneToOneDescriptor):

    def __get__(self, instance, cls=None):
        try:
            return super().__get__(instance, cls=cls)
        except self.RelatedObjectDoesNotExist:
            return None


class NullableReverseOneToOneDescriptor(ReverseOneToOneDescriptor):

    def __get__(self, instance, cls=None):
        try:
            return super().__get__(instance, cls=cls)
        except self.RelatedObjectDoesNotExist:
            return None


class NullableOneToOneField(OneToOneField):
    """ Modified version of Django's OneToOneField which sets the relation as nullable and doesn't
        raise DoesNotExist if the related object doesn't exist.
    """

    related_accessor_class = NullableReverseOneToOneDescriptor
    forward_related_accessor_class = NullableForwardOneToOneDescriptor

    def __init__(self, to, on_delete, to_field=None, **kwargs):
        kwargs["unique"] = True
        kwargs["null"] = True
        if "blank" not in kwargs:
            kwargs["blank"] = True
        super().__init__(to, on_delete, to_field=to_field, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if "unique" in kwargs:
            del kwargs["unique"]
        if "null" in kwargs:
            del kwargs["null"]
        return name, path, args, kwargs
