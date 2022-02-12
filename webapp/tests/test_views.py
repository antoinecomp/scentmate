from django.test import TestCase
from todo.models import Keyword
from django.contrib.auth.models import User # Required to assign User as a borrower
from django.urls import reverse


# Je veux tester que lorsque je fais une rerquête elle aboutie bien.
class QuizzTestCase(TestCase):
    def testQuizz(self):
        @classmethod
        def setUpTestData(cls):
            # Create keywords for pagination tests
            keywords = ["Fruity"]


class HomeViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class SimilarViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/similar/')
        self.assertEqual(response.status_code, 200)


class LoginViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')

        test_user1.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('profile'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'templates/todo/loginuser.html')


if __name__ == '__main__':
    unittest.main()
