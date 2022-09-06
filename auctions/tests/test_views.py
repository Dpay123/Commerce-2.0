from django.test import TestCase, Client
from django.urls import reverse
from auctions.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from auctions.views import check_if_seller, check_if_watched, check_if_winner

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.listing1 = Listing.objects.create(
            id= 0,
            item='Item 1',
            description='This is a description',
            starting_bid=34.99,
            category= 'Home',
            img= SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpg'),
            seller=self.user1
        )
        self.listing_url = reverse('listing', args=['0'])
        
    def test_check_if_watched(self):
        # set listing1 watched by user1
        Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        self.assertTrue(check_if_watched(self.user1, self.listing1))
        self.assertFalse(check_if_watched(self.user2, self.listing1))

    def test_check_if_seller(self):
        self.assertTrue(check_if_seller(self.user1, self.listing1))
        self.assertFalse(check_if_seller(self.user2, self.listing1))

    def test_check_if_winner_valid(self):
        winning_bid = Bid.objects.create(
            bidder=self.user2,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            category= 'Home',
            seller=self.user1,
            closed=True
        )
        # user2 is not seller and is current bidder
        # auction is closed
        self.assertTrue(check_if_winner(self.user2, listing2))
    
    def test_check_if_seller_is_winner(self):
        # user1 is seller, cannot be winner
        winning_bid = Bid.objects.create(
            bidder=self.user1,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            category= 'Home',
            seller=self.user1,
            closed=True
        )
        self.assertFalse(check_if_winner(self.user1, listing2))

    def test_listing_GET(self):
        response = self.client.get(self.listing_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')