from django import forms
from auctions.models import *
from django.db.models import *

class AddAuctionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label='Категорію не вибрано'
    class Meta:
        model=ActiveListings
        fields = ['lot_name', 'slug', 'lot_image', 'lot_description', 'price', 'cat']
        widgets = {
                'name': forms.TextInput(attrs={'class': 'form-input'}),
                'description': forms.Textarea(attrs={'cols':150, 'rows':10})
                
        }

class SetBetForm(forms.ModelForm):
    class Meta:
        model=Bet
        fields = [ 'bet_item', 'bet_price', 'last_bet_user']
        widgets = {
            #'bet_item': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_bet_user': forms.HiddenInput(), 
            'bet_item': forms.HiddenInput()
        }    
    
    def clean_bet_price(self, *args, **kwargs):
        bet_price=self.cleaned_data['bet_price'] 
        return bet_price

   
class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['title', 'text', 'comment_author', 'item']
        widgets = {
                'item': forms.HiddenInput(),
                'comment_author': forms.HiddenInput(),
                'text': forms.Textarea(attrs={'cols':100, 'rows':5}),
                'title': forms.Textarea(attrs={'cols':100, 'rows':1})
                }
#""" переопределили __init для автоподставления товара (post_pk) в поле формы ['item'] Comments: """
    """ def __init__(self, lot, *args, **kwargs):
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset=ActiveListings.objects.filter(lot_name__exact=lot) """