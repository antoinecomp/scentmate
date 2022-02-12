import unittest

from django.test import TestCase
from .todo.models import Keyword


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

# Je veux tester que lorsque je fais une rerquête elle aboutie bien.
class QuizzTestCase(TestCase):
    def testQuizz(self):
        @classmethod
        def setUpTestData(cls):
            # Create keywords for pagination tests
            keywords = ["Fruity"]

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/quiz/getmatch/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
