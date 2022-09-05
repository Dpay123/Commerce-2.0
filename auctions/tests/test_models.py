from django.test import TestCase
from auctions.models import *

class TestModels(TestCase):

    # will write test for User class if modified from default

    def setUp(self):
        self.user1 = User.objects.create()
        self.listing1 = Listing.objects.create(
            item= 'Item 1',
            starting_bid= 4.00,
            seller= self.user1
        )

    def test_listing_model_string_representation(self):
        self.assertEqual(str(self.listing1), self.listing1.item)