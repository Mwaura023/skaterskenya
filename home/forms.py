from django import forms
from .models import Event, Profile, SellerProfile, Merchandise, User, SellerProfile, MerchandiseCategory
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'skating_type', 'skill_level', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class EventForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],  # Matches the format used by datetime-local
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        label='Event Date & Time'
    )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'event_type',
            'skating_type',
            'location',
            'location_notes',
            'date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'location_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now():
            raise forms.ValidationError("The date and time cannot be in the past!")
        return date
    
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Profile, SellerProfile, Merchandise, MerchandiseCategory

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    USER_TYPES = [
        ('skater', 'Skater'),
        ('seller', 'Seller'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.RadioSelect)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'user_type')

    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        # Check if the email is already taken
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        
        return email

class SellerRegistrationForm(forms.ModelForm):
    product_categories = forms.ModelMultipleChoiceField(
        queryset=MerchandiseCategory.objects.all().order_by('name'),  # Now this will work
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select your product categories...'
        }),
        required=False,
        label="Product Categories"
    )

    class Meta:
        model = SellerProfile
        fields = ['business_name', 'description', 'contact_number', 'location', 'product_categories']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class MerchandiseForm(forms.ModelForm):
    class Meta:
        model = Merchandise
        fields = ['category', 'title', 'description', 'price', 
                 'condition', 'quantity', 'image', 'whatsapp_contact']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'whatsapp_contact': forms.TextInput(attrs={'placeholder': '2547XXXXXXXX'}),
        }