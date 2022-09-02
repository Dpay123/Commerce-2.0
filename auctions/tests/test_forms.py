from django.test import TestCase
from auctions.forms import *
from auctions.models import *

class TestForms(TestCase):

    def setUp(self):
        self.user1 = User.objects.create()

    def test_listing_form_valid_data(self):
        form = NewListingForm(data={
            'item': 'Item Title',
            'description': 'Item Description',
            'starting_bid': 1.00,
            'category': 'Home',
            'img': SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            'seller': User.objects.first()
        })
        self.assertTrue(form.is_valid())

    def test_listing_form_no_data(self):
        form = NewListingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)