from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor, ReverseSingleRelatedObjectDescriptor


class SmartSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    """ Reverse lookup object descriptor for SmartOneToOneField.
        If the lookup gets a DoesNotExist then it remembers this
        and (unlike a normal OneToOneField) the next time it is
        accessed it just raises straight away and doesn't bother
        with the DB query again.
    """
    
    def __get__(self, instance, instance_type=None):
        """ See if we've stored a DoesNotExist exception from last time,
            if so, just raise that.  Else... do the look up and store
            the DoesNotExist exception if we get one.
        """
        if getattr(instance, self.cache_name, None) is None:
            previous_exc = getattr(instance, self.get_exception_cache_name(), None)
            if previous_exc:
                raise previous_exc
        try:
            #This is effectively super(), but because it's __get__ it's a little bit magical...
            return SingleRelatedObjectDescriptor.__get__(self, instance, instance_type)
        except self.related.model.DoesNotExist, e:
            setattr(instance, self.get_exception_cache_name(), e)
            raise
    
    
    def get_exception_cache_name(self):
        return "_%s_does_not_exist_exception_cache" % self.related.get_accessor_name()


class SmartReverseSingleRelatedObjectDescriptor(ReverseSingleRelatedObjectDescriptor):
    """ Custom descriptor for the value of the SmartOneToOneField on the model which
        has the field on it.  Deals with clearing the exception cache when the field
        value is set (from the reverse side of the relationship).
        SmartSingleRelatedObjectDescriptor deals with clearing it when the value is
        set by doing a.b_name=b, and this descriptor deals with clearing it when the
        value is set by doing b.a_name=a.
    """
    
    def __set__(self, instance, value):
        self.delete_reverse_exception_cache(value)
        #This is effectively super(), but because it's a descriptor it's a little bit magical...
        return ReverseSingleRelatedObjectDescriptor.__set__(self, instance, value)
    
    
    def delete_reverse_exception_cache(self, related_instance):
        exception_cache_attr_name = self.get_reverse_exception_cache_name()
        try:
            delattr(related_instance, exception_cache_attr_name)
        except AttributeError:
            pass
    
    
    def get_reverse_exception_cache_name(self):
        return "_%s_does_not_exist_exception_cache" % self.field.related.get_accessor_name()



class NullableSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    """ Just like SingleRelatedObjectDescriptor but doesn't raise
        DoesNotExist if the object isn't found, just returns None
        instead of complaining.  Also then stores this None value
        and returns it next time instead of doing the DB look up again.
    """
    
    def __get__(self, instance, instance_type=None):
        try:
            return SingleRelatedObjectDescriptor.__get__(self, instance, instance_type)
        except self.related.model.DoesNotExist:
            setattr(instance, self.cache_name, None)
            return None



class OneOrNoneToOneField(OneToOneField):
    """
        Like a OneToOneField but allows the relation to work one way.
        So the model class which has this field on it *must* have the
        related object, but the model class which this field points
        *at* does not necessarily need to have the relationship back
        the other way.
    """
    description = "One-or-none-to-one relationship"
    
    
    def contribute_to_related_class(self, cls, related):
        setattr(
            cls,
            related.get_accessor_name(),
            NullableSingleRelatedObjectDescriptor(related)
        )




class SmartOneToOneField(OneToOneField):
    """ Like a OneToOneField, but when it does the reverse look up
        it remembers if it gets a DoesNotExist and then doesn't
        bother doing the DB query again when it's next accessed, it
        just re-raises straight away.  Note: it only remembers this
        on a per-instance basis; the memory of the missing related
        object is not persistent across separate loads of the object.
    """
    
    description = "Smart one-to-one relationship"
    
    def contribute_to_related_class(self, cls, related):
        setattr(
            cls,
            related.get_accessor_name(),
            SmartSingleRelatedObjectDescriptor(related)
        )
    
    
    def contribute_to_class(self, cls, name):
        super(SmartOneToOneField, self).contribute_to_class(cls, name)
        #Override the normal ReverseSingleRelatedObjectDescriptor with our magic one
        setattr(cls, self.name, SmartReverseSingleRelatedObjectDescriptor(self))











