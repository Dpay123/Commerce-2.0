from unicodedata import category
from django.test import TestCase, override_settings
from auctions.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil

TEST_DIR = 'test_data'

class TestModels(TestCase):

    # will write test for User class if modified from default

    def setUp(self):
        # create test users
        self.user1 = User.objects.create(username='user1')
        # create a test Category
        self.category1 = Category.objects.create(category="Test Category")
        # create a test listing 
        self.listing1 = Listing.objects.create(
            item= 'Item 1',
            starting_bid= 4.00,
            seller= self.user1,
            category= self.category1
        )
        # create a test bid
        self.new_bid = Bid.objects.create(
            bidder=self.user1,
            bid=10.01
        )

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_listing_model_valid_data(self):
        listing2 = Listing.objects.create(
            item='Item 2',
            description='This is a description',
            starting_bid=34.99,
            category= self.category1,
            img= SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpg'),
            seller=self.user1
        )
        self.assertEqual(listing2, Listing.objects.last())

    def test_listing_model_string_representation(self):
        self.assertEqual(str(self.listing1), self.listing1.item)

    def test_listing_model_get_current_bid_none(self):
        self.assertEquals(self.listing1.get_current_bid(), 0)

    def test_listing_model_get_current_bid(self):
        new_bid = Bid.objects.create(
            bidder=self.user1,
            bid=1.04
        )
        self.listing1.current_bid = new_bid
        self.assertEquals(self.listing1.get_current_bid(), 1.04)

    def test_watchlist(self):
        user2 = User.objects.create(username='user2')
        listing2 = Listing.objects.create(
            item= 'Item 2',
            starting_bid= 4.00,
            seller= user2,
            category= self.category1
        )
        Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        Watchlist.objects.create(
            user=self.user1,
            listing=listing2
        )
        Watchlist.objects.create(
            user=user2,
            listing=self.listing1
        )
        self.assertEquals(Watchlist.objects.filter(user=self.user1).count(), 2)
        self.assertEquals(Watchlist.objects.filter(user=user2).count(), 1)

    def test_watchlist_string_representation(self):
        watched_item = Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        self.assertEquals(str(watched_item), f'user1 is watching Item 1')

    def test_comment(self):
        user2 = User.objects.create(username='user2')
        Comment.objects.create(
            auction= self.listing1,
            author= self.user1,
            comment= 'This is a comment'
        )
        Comment.objects.create(
            auction= self.listing1,
            author= user2,
            comment= 'This is another comment'
        )
        self.assertEquals(Comment.objects.filter(auction=self.listing1).count(), 2)
        self.assertEquals(Comment.objects.filter(author=user2).count(), 1)

    def test_comment_string_representation(self):
        comment1 = Comment.objects.create(
            auction= self.listing1,
            author= self.user1,
            comment= 'This is a comment'
        )
        self.assertEquals(str(comment1), 'user1 commented on Item 1')

    def test_bid(self):
        self.assertEqual(self.new_bid, Bid.objects.first())

    def test_bid_string_representation(self):
        self.assertEquals(str(self.new_bid), "10.01 - user1")


def tearDownModule():
    print("\nDeleting temporary files...\n")
    try:
        shutil.rmtree(TEST_DIR)
    except OSError:
        pass