from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class User(AbstractUser):
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="skaterskenya_user_groups",
        related_query_name="skaterskenya_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="skaterskenya_user_permissions",
        related_query_name="skaterskenya_user",
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

class Profile(models.Model):
    SKATING_TYPES = [
        ('skateboard', 'Skateboard'),
        ('longboard', 'Longboard'),
        ('rollerblade', 'Rollerblade'),
        ('scooter', 'Scooter'),
        ('other', 'Other'),
    ]

    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.OneToOneField('home.User', on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    skating_type = models.CharField(max_length=100, choices=SKATING_TYPES, blank=True)
    skill_level = models.CharField(max_length=100, choices=SKILL_LEVELS, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    

class Event(models.Model):
    EVENT_TYPES = [
        ('MEET', 'Meetup'),
        ('COMP', 'Competition'),
        ('LESS', 'Lesson'),
        ('OTHR', 'Other'),
    ]
    
    SKATING_TYPES = [
        ('skateboard', 'Skateboard'),
        ('longboard', 'Longboard'),
        ('rollerblade', 'Rollerblade'),
        ('scooter', 'Scooter'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=4, choices=EVENT_TYPES)
    skating_type = models.CharField(max_length=20, choices=SKATING_TYPES)
    location = models.CharField(max_length=200)
    location_notes = models.TextField(blank=True)
    date = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, related_name='attending_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def maps_search_url(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.location}"


class SkateSpot(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skatespots')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
    

class MerchandiseCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=30, blank=True)
    
    def __str__(self):
        return self.name


class SellerProfile(models.Model):
    USER_TYPES = [
        ('skater', 'Skater'),
        ('seller', 'Merchandise Seller'),
        ('both', 'Both Skater and Seller')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='skater')
    business_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contact_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    product_categories = models.ManyToManyField(MerchandiseCategory, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} (Seller)"


class Merchandise(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Brand New'),
        ('used', 'Used - Good'),
        ('refurbished', 'Refurbished'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='merchandise')
    category = models.ForeignKey(MerchandiseCategory, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='merchandise/')
    date_posted = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    whatsapp_contact = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Format: 2547XXXXXXXX (Kenyan number with country code)"
    )
    
    def __str__(self):
        return f"{self.title} by {self.seller.username}"