from django.test import TestCase, Client
from django.urls import reverse
from auctions.models import *
from auctions.views import *

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username='user1')
        # assign password to created test user
        self.user1.set_password('pass')
        self.user1.save()
        self.user2 = User.objects.create(username='user2')
        self.user2.set_password('pass')
        self.user2.save()
        # set up test category
        self.category1 = Category.objects.create(category='test category')
        self.listing1 = Listing.objects.create(
            id= 0,
            item='Item 1',
            description='This is a description',
            starting_bid=34.99,
            seller=self.user1,
            category=self.category1
        )
        self.listing_url = reverse('listing', args=[self.listing1.id])
        self.category_url = reverse('category', args=[self.category1.id])
        self.watchlist_url = reverse('watchlist')
        self.user_listings_url = reverse('user listings')
        self.index_url = reverse('index')
        self.create_url = reverse('create')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.register_url = reverse('register')
        
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

    def test_check_if_winner_valid_bid_closed_auction(self):
        winning_bid = Bid.objects.create(
            bidder=self.user2,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            seller=self.user1,
            closed=True,
            category=self.category1
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
            seller=self.user1,
            closed=True,
            category= self.category1
        )
        self.assertFalse(check_if_winner(self.user1, listing2))

    def test_check_if_seller_valid_bid_open_auction(self):
        # cannot be winner if auction is not closed
        winning_bid = Bid.objects.create(
            bidder=self.user2,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            seller=self.user1,
            closed=False,
            category=self.category1
        )
        self.assertFalse(check_if_winner(self.user2, listing2))

    def test_listing_GET(self):
        response = self.client.get(self.listing_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')

    def test_category_GET(self):
        # represents a search for items by category
        response = self.client.get(self.category_url)
        self.assertEquals(response.status_code, 200)
        # should return index page
        self.assertTemplateUsed(response, "auctions/index.html")
        # should return queryset with all Listings in 0 category
        self.assertQuerysetEqual(response.context['listings'], Listing.objects.filter(category=self.category1))

    def test_watchlist_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # add test item to watchlist
        Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        response = self.client.get(self.watchlist_url)
        self.assertEquals(response.status_code, 200)
        # should return watchlist page
        self.assertTemplateUsed(response, "auctions/watchlist.html")
        # should return a queryset of all items in user watchlist
        self.assertQuerysetEqual(response.context['watchlist'], Watchlist.objects.filter(user=self.user1))

    def test_user_listings_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        response = self.client.get(self.user_listings_url)
        self.assertEquals(response.status_code, 200)
        # should return user_listings page
        self.assertTemplateUsed(response, "auctions/user_listings.html")
        # should return a queryset of all items listed by user
        self.assertQuerysetEqual(response.context['user_listings'], Listing.objects.filter(seller=self.user1))

    def test_index_GET(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        # should return index page
        self.assertTemplateUsed(response, 'auctions/index.html')
        # should return queryset with all Listings in db
        self.assertQuerysetEqual(response.context['listings'], Listing.objects.all())

    def test_create_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 200)
        # should return create page
        self.assertTemplateUsed(response, 'auctions/create.html')
        # should pass the NewListingForm as context
        self.assertIsInstance(response.context['form'], NewListingForm)

    def test_create_POST_valid(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # test form data
        response = self.client.post(self.create_url, {
            'item': 'Test Item',
            'starting_bid': 1.00,
            'seller': self.user1.id,
            'category': self.category1.id
        })
        # valid form data should be saved as object
        self.assertTrue(Listing.objects.filter(item='Test Item').exists())
        # valid form data should redirect to index
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_create_POST_invalid(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # test invalid form data
        response = self.client.post(self.create_url, {
            'item': 'Test Item',
            'starting_bid': -1
        })
        # should return to create page
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/create.html")

    def test_listing_POST_not_logged_in(self):
        response = self.client.post(self.listing_url, {})
        # should return to listing page with error message
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/listing.html")
        self.assertEquals(response.context['error'], "You must be logged in")

    def test_listing_POST_close(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # test close auction functionality
        response = self.client.post(self.listing_url, {
            'button': "Close"
        })
        # test listing closed
        self.assertTrue(Listing.objects.get(pk=0).closed)
        # successful close should redirect back to listing page
        self.assertRedirects(response, self.listing_url, status_code=302)
    
    def test_listing_POST_add_to_watchlist(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # simulate watchlist button click
        response = self.client.post(self.listing_url, {
            'button': "Watchlist"
        })
        # test watchlist added
        self.assertTrue(Watchlist.objects.filter(user=self.user1, listing=self.listing1).exists())
        # successful close should redirect back to listing page
        self.assertRedirects(response, self.listing_url, status_code=302)

    def test_listing_POST_remove_from_watchlist(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # create watchlist item
        Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        # simulate watchlist button click
        response = self.client.post(self.listing_url, {
            'button': "Watchlist"
        })
        # test watchlist removed
        self.assertFalse(Watchlist.objects.filter(user=self.user1, listing=self.listing1).exists())
        # successful close should redirect back to listing page
        self.assertRedirects(response, self.listing_url, status_code=302)

    def test_listing_POST_valid_comment(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # simulate comment button click
        response = self.client.post(self.listing_url, {
            'button': 'comment',
            'comment': 'this is a comment',
            'author': self.user1.id,
            'auction': self.listing1.id
        })
        # test comment created
        self.assertTrue(Comment.objects.filter(comment='this is a comment', author=self.user1, auction=self.listing1).exists())

    def test_listing_POST_invalid_comment(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # simulate comment button click with invalid data (blank comment)
        response = self.client.post(self.listing_url, {
            'button': 'comment',
            'author': self.user1.id,
            'auction': self.listing1.id
        })
        # test comment not created
        self.assertFalse(Comment.objects.filter(author=self.user1).exists())

    def test_listing_POST_valid_bid_valid(self):
        # log in user (that is not seller)
        self.client.login(username='user2', password='pass')
        # simulate bid button click
        response = self.client.post(self.listing_url, {
            'bidder': self.user2.id,
            'bid': 35.00
        })
        # check bid created
        self.assertEquals(len(Bid.objects.all()), 1)
        # check listing current bid updated
        self.assertEquals(Listing.objects.first().get_current_bid(), 35.00)
        # successful bid should redirect to listing 
        self.assertRedirects(response, self.listing_url, status_code=302)

    def test_listing_POST_valid_bid_lower_than_starting_bid(self):
        # log in user (that is not seller)
        self.client.login(username='user2', password='pass')
        # simulate bid button click
        response = self.client.post(self.listing_url, {
            'bidder': self.user2.id,
            'bid': 32.00
        })
        # check bid not created
        self.assertEquals(len(Bid.objects.all()), 0)
        # invalid bid returns to listing page with error message
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/listing.html")
        self.assertEquals(response.context['bid_error'], "Bid must exceed starting bid and current bid")

    def test_listing_POST_valid_bid_lower_than_current_bid(self):
        listing_url1 = reverse('listing', args=['1'])
        # log in user (that is not seller)
        self.client.login(username='user2', password='pass')
        # create new listing with current bid
        Bid.objects.create(
            bid=35.50,
            bidder=self.user2
        )
        Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=Bid.objects.first(),
            seller=self.user1,
            category=self.category1
        )
        # simulate bid button click with bid lower than current
        response = self.client.post(listing_url1, {
            'bidder': self.user2.id,
            'bid': 35.25
        })
        # check 2nd bid not created
        self.assertEquals(len(Bid.objects.filter(bidder=self.user2)), 1)
        # invalid bid returns to listing page with error message
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/listing.html")
        self.assertEquals(response.context['bid_error'], "Bid must exceed current")

    def test_login_view_GET(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")

    def test_login_view_POST_valid_user(self):
        response = self.client.post(self.login_url, {
            'username': self.user1,
            'password': 'pass'
        })
        # check valid login
        self.assertTrue(self.user1.is_authenticated)
        # valid login should redirect to index page
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_login_view_POST_invalid_user(self):
        response = self.client.post(self.login_url, {
            'username': 'invalid',
            'password': 'invalid'
        })
        # invalid login should return the login page
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")
        self.assertEquals(response.context['message'], "Invalid username and/or password.")

    def test_login_view_POST_invalid_password(self):
        response = self.client.post(self.login_url, {
            'username': self.user1,
            'password': 'invalid'
        })
        # invalid login should return the login page
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")
        self.assertEquals(response.context['message'], "Invalid username and/or password.")

    def test_logout_view_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        response = self.client.get(self.logout_url)
        # default redirect status code is 302
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_register_GET(self):
        response = self.client.get(self.register_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/register.html")

    def test_register_POST_valid(self):
        response = self.client.post(self.register_url, {
            'username': 'user3',
            'email': 'email@email.com',
            'password': 'pass',
            'confirmation': 'pass'
        })
        user = User.objects.get(username='user3')
        # check valid registration
        self.assertTrue(user.is_active)
        # check valid login
        self.assertTrue(user.is_authenticated)
        # valid login should redirect to index page
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_register_POST_invalid_pass_confirmation(self):
        response = self.client.post(self.register_url, {
            'username': 'user3',
            'email': 'email@email.com',
            'password': 'pass',
            'confirmation': 'not pass'
        })
        # check user was not created
        self.assertEquals(len(User.objects.filter(username='user3')), 0)
        # invalid registration should return register page with error
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/register.html")
        self.assertEquals(response.context['message'], "Passwords must match.")

    def test_register_POST_username_taken(self):
        response = self.client.post(self.register_url, {
            'username': 'user1',
            'email': 'notsaved@email.com',
            'password': 'pass',
            'confirmation': 'pass'
        })
        # username taken = Integrity Error, returns register page with error message
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/register.html")
        self.assertEquals(response.context['message'], "Username already taken.")