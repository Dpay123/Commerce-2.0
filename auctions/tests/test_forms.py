from django.test import TestCase
from auctions.forms import *
from auctions.models import *

class TestForms(TestCase):

    def setUp(self):
        self.user1 = User.objects.create()
        self.item1 = Listing.objects.create(
            item='Item 1',
            starting_bid=4.22,
            seller=self.user1
        )

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

    def test_bid_form_valid_data(self):
        # set up a bidder
        user2 = User.objects.create(username='bidder')
        form = NewBidForm(data={
            'bidder': user2,
            'bidding_on': self.item1,
            'bid': 4.64
        })
        self.assertTrue(form.is_valid())

    def test_bid_form_no_data(self):
        form = NewBidForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)

    def test_comment_form_valid_data(self):
        form = NewCommentForm(data={
            'auction': self.item1,
            'author': self.user1,
            'comment': 'This is a comment'
        })
        self.assertTrue(form.is_valid())

    def test_comment_form_no_data(self):
        form = NewCommentForm(data={})
        self.assertEqual(len(form.errors), 3)
