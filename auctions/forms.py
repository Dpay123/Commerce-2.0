from django.forms import ModelForm, HiddenInput
from .models import *
from django.core.files.uploadedfile import SimpleUploadedFile

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item', 'description', 'starting_bid', 'category', 'img', 'seller']
        widgets = {'seller': HiddenInput()}

class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

class NewCommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']

class NewWatchForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = ['user', 'listing']