from django.db import models
from django.test import TestCase

from .fields import SmartOneToOneField


class Flag(models.Model):
    pass

class Flagpole(models.Model):
    """ A pole on which a flag sits. """
    flag = SmartOneToOneField(Flag)

class Country(models.Model):
    """ A country, which always has a flag.  Although
        occasionally you can find a flag which doesn't
        belong to a country, so flag.country will raise
        DoesNotExist.
    """
    flag = SmartOneToOneField(Flag)



class UsefulTestSTuff(object):
    """ Mixin class with handy methods for tests. """
    
    def reload_from_db(self, country):
        return country.__class__.objects.get(pk=country.pk)



class SmartOneToOneFieldTest(TestCase, UsefulTestSTuff):
    """ Tests for the SmartOneToOneField. """
    
    def test_basic_functionality(self):
        #Create 2 objects with one pointing to the other
        flag = Flag.objects.create()
        country = Country.objects.create(
            flag=flag
        )
        #Check that they point to each other
        self.assertEqual(country.flag, flag)
        self.assertEqual(flag.country, country)
        #reload the object from the DB and check that everything is still good
        country = self.reload_from_db(country)
        flag = self.reload_from_db(flag)
        self.assertEqual(country.flag, flag)
        self.assertEqual(flag.country, country)
    
    
    def test_raises_if_does_not_exist_but_not_once_set(self):
        """ Test that the reverse lookup correctly raises DoesNotExist
            when the object doesn't exist, but that once it has been
            set it doesn't raise it again.
        """
        #Create a Flag object, but don't have a Country pointing at it,
        #so when we access flag.country it will raise DoesNotExist
        flag = Flag.objects.create()
        self.assertRaises(Country.DoesNotExist, getattr, flag, 'country')
        #Now create a Country that points at our Flag object...
        country = Country.objects.create(flag=flag)
        flag = self.reload_from_db(flag)
        #Accessing flag.country should no longer raise...
        self.assertEqual(flag.country, country)
    
    
    def test_correct_exceptions_are_remembered(self):
        """ Test that when we store the previously raised exceptions
            that exceptions for different fields are not confused.
        """
        flag = Flag.objects.create()
        self.assertRaises(Country.DoesNotExist, getattr, flag, 'country')
        self.assertRaises(Flagpole.DoesNotExist, getattr, flag, 'flagpole')








