from django.forms import ModelForm, HiddenInput, NumberInput, ModelChoiceField
from .models import *

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item', 'description', 'starting_bid', 'category', 'img', 'seller']
        widgets = {
            'seller': HiddenInput(),
            'starting_bid': NumberInput(attrs={'step': 'any'})
        }

        def __init__(self, *args, **kwargs):
            super(NewListingForm, self).__init__(*args, **kwargs)
            self.fields['category'].widget = ModelChoiceField(queryset=Category.objects.all())

class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid', 'bidder']
        widgets = {
            'bidder': HiddenInput()
        }

class NewCommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['comment', 'auction', 'author']
        widgets = {
            'auction': HiddenInput(),
            'author': HiddenInput()
        }

class NewWatchForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = ['user', 'listing']