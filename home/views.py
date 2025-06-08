from django.shortcuts import render, redirect, get_object_or_404, reverse
# from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
User = get_user_model() 

from django.contrib.auth import login, authenticate # Add this import
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from .models import Profile, Event, SkateSpot
from .models import SellerProfile, Merchandise, MerchandiseCategory, Activity
from .forms import SellerRegistrationForm, MerchandiseForm, CustomUserCreationForm, ProfileUpdateForm, EventForm
from django.contrib.admin.views.decorators import staff_member_required


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator




# Community data configuration
COMMUNITY_DATA = {
    'skateboard': {
        'name': 'Skateboard',
        'icon': 'skateboard',
        'description': 'Street and park skaters pushing the limits',
        'slug': 'skateboard',
        'image': 'skateboard.jpg'
    },
    'longboard': {
        'name': 'Longboard',
        'icon': 'longboard',
        'description': 'Downhill and cruising enthusiasts',
        'slug': 'longboard',
        'image': 'longboard.jpg'
    },
    'rollerblade': {
        'name': 'Rollerblade',
        'icon': 'roller-skate',
        'description': 'Urban flow and aggressive skating',
        'slug': 'rollerblade',
        'image': 'rollerblade.jpg'
    },
    'scooter': {
        'name': 'Scooter',
        'icon': 'scooter',
        'description': 'Trick riders and street performers',
        'slug': 'scooter',
        'image': 'scooter.jpg'
    },
    'other': {
        'name': 'Other',
        'icon': 'skating',
        'description': 'All other skating enthusiasts',
        'slug': 'other',
        'image': 'skate-group.jpg'
    }
}


@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    User = get_user_model()
    
    # User stats
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=now.date()).count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Profile stats
    skating_types = {
        'skateboard': Profile.objects.filter(skating_type='skateboard').count(),
        'longboard': Profile.objects.filter(skating_type='longboard').count(),
        'rollerblade': Profile.objects.filter(skating_type='rollerblade').count(),
        'scooter': Profile.objects.filter(skating_type='scooter').count(),
    }
    
    # Event stats
    active_events = Event.objects.filter(date__gte=now).count()
    upcoming_events_list = Event.objects.filter(date__gte=now).order_by('date')[:5]
    upcoming_events = upcoming_events_list.count()
    
    # Merchandise stats
    total_merchandise = Merchandise.objects.count()
    new_merchandise = Merchandise.objects.filter(date_posted__date=now.date()).count()
    recent_merchandise = Merchandise.objects.order_by('-date_posted')[:5]
    
    # Seller stats
    total_sellers = SellerProfile.objects.count()
    verified_sellers = SellerProfile.objects.filter(verified=True).count()
    
    # Activity stats
    recent_activities = Activity.objects.order_by('-date')[:5]
    
    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'recent_users': recent_users,
        'skating_types': skating_types,
        'active_events': active_events,
        'upcoming_events': upcoming_events,
        'upcoming_events_list': upcoming_events_list,
        'total_merchandise': total_merchandise,
        'new_merchandise': new_merchandise,
        'recent_merchandise': recent_merchandise,
        'total_sellers': total_sellers,
        'verified_sellers': verified_sellers,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'home/admin_dashboard.html', context)


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user but do not activate
            user = form.save(commit=False)
            user.is_active = False  # User inactive until email verification
            user.save()
            
            # Create user profile (generic profile for all users)
            Profile.objects.get_or_create(user=user)
            
            # Handle seller-specific creation
            if form.cleaned_data['user_type'] == 'seller':
                SellerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'user_type': 'seller',
                        'business_name': f"{user.username}'s Skate Shop"
                    }
                )
            
            # Send email verification
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = f"{request.scheme}://{request.get_host()}/verify-email/{uid}/{token}/"
            
            subject = "Verify Your Email for Skaters Kenya"
            message = render_to_string('emails/verify_email.html', {
                'user': user,
                'verification_url': verification_url
            })
            
            # Send email asynchronously
            send_mail(
                subject,
                message,
                'mwaurasony023@gmail.com',
                [user.email],
                html_message=message,
                fail_silently=False
            )
            
            messages.info(request, 'Please check your email to verify your account.')
            return redirect('email-sent')  # Redirect to a page that informs the user
    else:
        form = CustomUserCreationForm()
    
    # Render the signup page
    return render(request, 'home/signup.html', {'form': form})

def logged_out_view(request):
    return render(request, 'home/logout.html')

def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your email has been verified! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'The verification link was invalid or has expired.')
        return redirect('homepage')

class CustomLoginView(LoginView):
    template_name = 'home/login.html'
    
    def form_valid(self, form):
        """Handle successful login with robust profile checking"""
        response = super().form_valid(form)
        user = self.request.user
        
        # Safely check for profile without raising exceptions
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user)
            messages.info(
                self.request, 
                "Welcome! Please complete your profile details",
                extra_tags='alert-info'
            )
            return redirect('profile-update')
        
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Login failed. Please check your credentials",
            extra_tags='alert-danger'
        )
        return super().form_invalid(form)
    


User = get_user_model()

@login_required
def profile(request, username):
    # Get the user by username
    user = get_object_or_404(User, username=username)

    # 🔐 Prevent crash if profile doesn't exist
    profile, _ = Profile.objects.get_or_create(user=user)

    # Check if current user is the profile owner
    is_owner = request.user == user

    # Related user stats
    events_attended = Event.objects.filter(attendees=user).count()
    spots_added = SkateSpot.objects.filter(added_by=user).count()
    years_skating = 3  # Replace with real logic if needed
    recent_activity = Activity.objects.filter(user=user).order_by('-date')[:10]

    context = {
        'profile': profile,
        'is_owner': is_owner,
        'events_attended': events_attended,
        'spots_added': spots_added,
        'years_skating': years_skating,
        'recent_activity': recent_activity,
    }

    return render(request, 'home/profile.html', context)



@login_required
def profile_update(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'home/profile_update.html', {'form': form})

def homepage(request):
    user = request.user
    profile = None
    profile_complete = False

    if user.is_authenticated:
        try:
            profile = user.profile
            if profile.skating_type and profile.location:
                profile_complete = True
        except Profile.DoesNotExist:
            pass

    # Get counts for all communities
    counts = Profile.objects.values('skating_type').annotate(count=Count('skating_type'))
    count_dict = {c['skating_type']: c['count'] for c in counts}

    # Build featured communities (first 3)
    featured = []
    for code in list(COMMUNITY_DATA.keys())[:3]:
        community = COMMUNITY_DATA[code].copy()
        community.update({
            'code': code,
            'member_count': count_dict.get(code, 0)
        })
        featured.append(community)

    return render(request, 'home/homepage.html', {
        'featured_communities': featured,
        'profile': profile,
        'profile_complete': profile_complete
    })


def all_communities(request):
    """
    Display all available skating communities with member counts.
    
    Context:
        communities: List of dictionaries containing:
            - code: Community code (e.g., 'skateboard')
            - name: Display name
            - icon: FontAwesome icon class
            - description: Community description
            - slug: URL slug
            - image: Image filename
            - member_count: Number of members in this community
    """
    # Get member counts for each community type
    counts = Profile.objects.values('skating_type').annotate(count=Count('skating_type'))
    count_dict = {c['skating_type']: c['count'] for c in counts}
    
    # Build community list with member counts
    communities = [
        {
            **data,  # Include all original COMMUNITY_DATA fields
            'code': code,
            'member_count': count_dict.get(code, 0)
        }
        for code, data in COMMUNITY_DATA.items()
    ]
    
    return render(request, 'home/all_communities.html', {
        'communities': communities
    })

def community_detail(request, slug):
    """Detailed view for a specific community"""
    community = next((c for c in COMMUNITY_DATA.values() if c['slug'] == slug), None)
    if not community:
        raise Http404("Community not found")
    
    # Get member count
    member_count = Profile.objects.filter(skating_type=community['slug']).count()
    
    # Get upcoming events with URL safety check
    events = Event.objects.filter(
        skating_type=community['slug'],
        date__gte=timezone.now()
    ).order_by('date')[:3]
    
    # Prepare events data with safe URLs
    upcoming_events = []
    for event in events:
        if event.pk:  # Only include events with valid primary keys
            upcoming_events.append({
                'pk': event.pk,
                'title': event.title,
                'location': event.location,
                'date': event.date
            })
    
    context = {
        'community': community,
        'member_count': member_count,
        'upcoming_events': upcoming_events,
        'is_current_community': request.user.is_authenticated and 
                              hasattr(request.user, 'profile') and 
                              request.user.profile.skating_type == community['slug']
    }
    
    return render(request, 'home/community_detail.html', context)



def skater_category(request, category):
    """View showing all members of a specific skating community"""
    if category not in COMMUNITY_DATA:
        raise Http404("Category not found")
    
    # Debug: Print the category being requested
    print(f"Requested category: {category}")
    
    community = COMMUNITY_DATA[category]
    
    # Get all profiles for this community with related user data
    skaters = Profile.objects.filter(
        skating_type=category
    ).select_related('user')
    
    # Debug: Print the raw query and count
    print(f"SQL Query: {str(skaters.query)}")
    print(f"Found {skaters.count()} members for {category}")
    
    # Prepare profile data with safe image URLs
    profiles_with_images = []
    for profile in skaters:
        try:
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else '/static/images/default-profile.jpg'
        except ValueError:
            profile_picture_url = '/static/images/default-profile.jpg'
            
        profile_data = {
            'profile': profile,
            'profile_picture_url': profile_picture_url,
            'user': profile.user,
            'location': profile.location or "Location not specified",
            'skill_level': profile.get_skill_level_display()
        }
        profiles_with_images.append(profile_data)
    
    context = {
        'profiles': profiles_with_images,
        'community': community,
        'category_name': community['name'],
        'category_slug': category,
        'is_current_community': request.user.is_authenticated and 
                              hasattr(request.user, 'profile') and 
                              request.user.profile.skating_type == category,
        'is_exploring': True
    }
    
    return render(request, 'home/skater_category.html', context)


def search_skaters(request):
    query = request.GET.get('q', '')
    skaters = Profile.objects.filter(
        Q(user__username__icontains=query) |
        Q(location__icontains=query) |
        Q(skating_type__icontains=query)
    ) if query else Profile.objects.none()
    
    return render(request, 'home/search_skaters.html', {
        'skaters': skaters,
        'query': query
    })

class EventListView(ListView):
    model = Event
    template_name = 'home/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(date__gte=timezone.now())
        if skating_type := self.request.GET.get('skating_type'):
            queryset = queryset.filter(skating_type=skating_type)
        return queryset.order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skating_types'] = Profile.SKATING_TYPES  # Add skating types to context
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'home/event_form.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'home/event_form.html'
    success_url = reverse_lazy('event-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.creator != request.user:
            return redirect('event-list')
        return super().dispatch(request, *args, **kwargs)

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'home/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'home/event_detail.html', {
        'event': event,
        'is_attending': request.user.is_authenticated and 
                       request.user in event.attendees.all()
    })

@login_required
def attend_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
        messages.success(request, f"You're no longer attending {event.title}")
    else:
        event.attendees.add(request.user)
        messages.success(request, f"You're now attending {event.title}")
    return redirect('event-detail', pk=pk)




#sellers views
@login_required
def become_seller(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            seller_profile = form.save(commit=False)
            seller_profile.user = request.user
            seller_profile.user_type = 'seller'
            seller_profile.save()
            
            # Update the main profile if needed
            profile = request.user.profile
            profile.save()
            
            messages.success(request, 'Seller profile created successfully!')
            return redirect('seller_dashboard')
    else:
        form = SellerRegistrationForm()
    
    return render(request, 'home/become_seller.html', {'form': form})

@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('become_seller')
    
    merchandise = Merchandise.objects.filter(seller=request.user)
    return render(request, 'home/seller_dashboard.html', {
        'merchandise': merchandise
    })

@login_required
def add_merchandise(request):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('become_seller')
    
    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES)
        if form.is_valid():
            merchandise = form.save(commit=False)
            merchandise.seller = request.user
            merchandise.save()
            messages.success(request, 'Merchandise added successfully!')
            return redirect('seller_dashboard')
    else:
        form = MerchandiseForm()
    
    return render(request, 'home/add_merchandise.html', {'form': form})

def merchandise_list(request):
    # Get all available merchandise
    merchandise = Merchandise.objects.filter(available=True)
    
    # Get all categories for filter dropdown
    categories = MerchandiseCategory.objects.all()
    
    # Handle category filtering
    category_id = request.GET.get('category')
    if category_id:
        merchandise = merchandise.filter(category__id=category_id)
    
    # Handle search queries
    search_query = request.GET.get('q')
    if search_query:
        merchandise = merchandise.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    return render(request, 'home/merchandise_list.html', {
        'merchandise': merchandise,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query or ''
    })

def merchandise_detail(request, pk):
    item = get_object_or_404(Merchandise, pk=pk)
    return render(request, 'home/merchandise_detail.html', {
        'item': item,
        'similar_items': Merchandise.objects.filter(
            category=item.category,
            available=True
        ).exclude(pk=pk)[:4]
    })

@login_required
def edit_merchandise(request, pk):
    item = get_object_or_404(Merchandise, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('seller_dashboard')
    else:
        form = MerchandiseForm(instance=item)
    return render(request, 'home/merchandise_form.html', {'form': form, 'editing': True})

@login_required
def delete_merchandise(request, pk):
    item = get_object_or_404(Merchandise, pk=pk, seller=request.user)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('seller_dashboard')
    return render(request, 'home/merchandise_confirm_delete.html', {'item': item})

@login_required
def toggle_merchandise(request, pk):
    item = get_object_or_404(Merchandise, pk=pk, seller=request.user)
    item.available = not item.available
    item.save()
    status = "available" if item.available else "unavailable"
    messages.success(request, f'Item marked as {status}')
    return redirect('seller_dashboard')

@login_required
def update_seller_profile(request):
    try:
        seller_profile = request.user.sellerprofile
    except SellerProfile.DoesNotExist:
        return redirect('become_seller')
    
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, instance=seller_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seller profile updated!')
            return redirect('seller_dashboard')
    else:
        form = SellerRegistrationForm(instance=seller_profile)
    
    return render(request, 'home/update_seller_profile.html', {'form': form})


def merchandise_detail(request, pk):
    item = get_object_or_404(Merchandise.objects.select_related('seller__sellerprofile', 'category'), pk=pk)
    
    # Get seller info or defaults
    seller_profile = getattr(item.seller, 'sellerprofile', None)
    location = seller_profile.location if seller_profile else "Location not specified"
    contact = seller_profile.contact_number if seller_profile else "Contact seller via profile"
    business_name = seller_profile.business_name if seller_profile else f"{item.seller.username}'s Shop"
    
    similar_items = Merchandise.objects.filter(
        category=item.category,
        available=True
    ).exclude(pk=pk)[:4]
    
    return render(request, 'home/merchandise_detail.html', {
        'item': item,
        'seller_profile': seller_profile,
        'business_name': business_name,
        'location': location,
        'contact': contact,
        'similar_items': similar_items,
        'is_seller': hasattr(request.user, 'sellerprofile')
    })