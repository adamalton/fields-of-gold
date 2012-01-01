from django.db import models
from django.test import TestCase

from .fields import SmartOneToOneField


class Dog(models.Model):
    pass

class Cat(models.Model):
    pass

class Human(models.Model):
    """ Someone who has pets.  Always one cat and one dog.
        Note: there are sometimes stray dogs and cats which
        don't belong to a human.  These can cause Human.DoesNotExist
        when you try to find the owner.
    """
    dog = SmartOneToOneField(Dog)



class UsefulTestSTuff(object):
    """ Mixin class with handy methods for tests. """
    
    def reload_from_db(self, human):
        return human.__class__.objects.get(pk=human.pk)



class SmartOneToOneFieldTest(TestCase, UsefulTestSTuff):
    """ Tests for the SmartOneToOneField. """
    
    def test_basic_functionality(self):
        #Create 2 objects with one pointing to the other
        dog = Dog.objects.create()
        human = Human.objects.create(
            dog=dog
        )
        #Check that they point to each other
        self.assertEqual(human.dog, dog)
        self.assertEqual(dog.human, human)
        #reload the object from the DB and check that everything is still good
        human = self.reload_from_db(human)
        dog = self.reload_from_db(dog)
        self.assertEqual(human.dog, dog)
        self.assertEqual(dog.human, human)
    
    
    def test_raises_if_does_not_exist_but_not_once_set(self):
        """ Test that the reverse lookup correctly raises DoesNotExist
            when the object doesn't exist, but that once it has been
            set it doesn't raise it again.
        """
        #Create a Dog object, but don't have a Human pointing at it,
        #so when we access dog.human it will raise DoesNotExist
        dog = Dog.objects.create()
        self.assertRaises(Human.DoesNotExist, getattr, dog, 'human')
        #Now create a Human that points at our Dog object...
        human = Human.objects.create(dog=dog)
        dog = self.reload_from_db(dog)
        #Accessing dog.human should no longer raise...
        self.assertEqual(dog.human, human)








