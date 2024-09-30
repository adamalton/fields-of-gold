# Third Party
from django.db import connection
from django.test import TestCase

class ExtraModelsTestCase(TestCase):
    """ Test case that sets up and destroys DB table(s) for additional models that are used only
        for the tests.
    """

    test_models = []

    @classmethod
    def setUpClass(cls):
        with connection.schema_editor() as schema_editor:
            for model in cls.test_models:
                schema_editor.create_model(model)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        with connection.schema_editor() as schema_editor:
            for model in cls.test_models:
                schema_editor.delete_model(model)
