from django import forms
from django.contrib.auth.models import User
from .models import Profile, Campaign, Donation, ContactQuery, RecipientRequest

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'gender', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ✅ Pass user in view
        super(ProfileForm, self).__init__(*args, **kwargs)

        if user and not user.is_superuser:
            # ✅ Restrict normal users to donor and recipient only
            self.fields['role'].choices = [
                ('donor', 'Donor'),
                ('recipient', 'Recipient'),
            ]

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'goal_amount', 'category']

# class DonationForm(forms.ModelForm):
#     class Meta:
#         model = Donation
#         fields = ['campaign', 'amount']

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donation_type', 'name', 'phone', 'email', 'campaign', 'purpose', 'amount', 'address']
        widgets = {
            'donation_type': forms.RadioSelect()
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactQuery
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class ReplyForm(forms.Form):
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class RecipientRequestForm(forms.ModelForm):
    class Meta:
        model = RecipientRequest
        fields = ['aadhaar_number', 'ration_card_number', 'aadhaar_file', 'ration_card_file', 'family_income', 'description']
