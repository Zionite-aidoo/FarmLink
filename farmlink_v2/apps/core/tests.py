from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import ContactMessage


class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_renders(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Good food')

    def test_about_page_renders(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our story')

    def test_contact_form_submission(self):
        response = self.client.post(reverse('core:contact'), {
            'name': 'Kojo Antwi',
            'phone': '0241234567',
            'email': 'kojo@example.com',
            'message': 'Hello, I want to partner with FarmLink in Kumasi.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Kojo Antwi')
        self.assertEqual(msg.email, 'kojo@example.com')

