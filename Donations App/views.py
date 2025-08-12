from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404,render, redirect
from .forms import UserRegisterForm, ProfileForm, CampaignForm, DonationForm,ContactForm, ReplyForm,RecipientRequestForm
from .models import Campaign, Donation,Profile, ContactQuery,Organization, RecipientRequest
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from decimal import Decimal

from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  # ✅ FIXED
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def profile_view(request):
    # Create a profile if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})
@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('complete_profile')

    organizations = Organization.objects.all()

    context = {
        'profile': profile,
        'organizations': organizations,
    }

    if profile.role == 'admin':
        return render(request, 'dashboard_admin.html', context)
    elif profile.role == 'donor':
        return render(request, 'dashboard_donor.html', context)
    elif profile.role == 'recipient':
        return render(request, 'dashboard_recipient.html', context)

    return render(request, 'dashboard.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    original_role = profile.role

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            updated_profile = form.save(commit=False)

            # ✅ Backend safety: Prevent normal users from setting admin
            if not request.user.is_superuser and updated_profile.role not in ['donor', 'recipient']:
                updated_profile.role = original_role  # Revert role change

            updated_profile.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'edit_profile.html', {'form': form})

@staff_member_required
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()
            return redirect('dashboard')
    else:
        form = CampaignForm()
    return render(request, 'create_campaign.html', {'form': form})

@staff_member_required
def delete_campaign_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    if request.method == 'POST':
        if campaign.donation_set.exists():
            messages.error(request, "Cannot delete. Donations already exist for this campaign.")
        else:
            campaign.delete()
            messages.success(request, f"Campaign '{campaign.title}' has been deleted.")
        return redirect('dashboard')
    
    return render(request, 'delete_campaign.html', {'campaign': campaign})


@staff_member_required
def edit_campaign_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated successfully.')
            return redirect('dashboard')
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'edit_campaign.html', {'form': form, 'campaign': campaign})

# @login_required
# def donate(request):
#     if request.method == 'POST':
#         form = DonationForm(request.POST)
#         if form.is_valid():
#             donation = form.save(commit=False)
#             donation.donor = request.user
#             campaign = donation.campaign
#             campaign.collected_amount += donation.amount
#             campaign.save()
#             donation.save()
#             return redirect('dashboard')
#     else:
#         form = DonationForm()
#     return render(request, 'donate.html', {'form': form})


@login_required
def my_donations_view(request):
    donations = Donation.objects.filter(user=request.user)
    return render(request, 'my_donations.html', {'donations': donations})


@staff_member_required  # Only allow admin/staff to view
def all_donations_view(request):
    donations = Donation.objects.select_related('donor', 'campaign').order_by('-donated_at')
    return render(request, 'all_donations.html', {'donations': donations})

# views.py
@staff_member_required
def donations_list(request):
    donations = [
        {
            "donor": "Priya Sharma",
            "type": "Monetary",
            "amount": "₹3,000",
            "campaign": "Sponsor a Child's Education",
            "message": "Use this for purchasing textbooks.",
            "anonymous": False
        },
        {
            "donor": "Anonymous",
            "type": "In-Kind",
            "amount": "50 kg rice, 20 L oil (₹4,500 est.)",
            "campaign": "Feed the Homeless",
            "message": "",
            "anonymous": True
        },
        {
            "donor": "Mahesh Kumar",
            "type": "In-Kind",
            "amount": "10 blankets, 5 jackets (₹6,000 est.)",
            "campaign": "Warmth for the Needy",
            "message": "Hope this keeps someone warm this winter.",
            "anonymous": False
        },
        {
            "donor": "Dr. Ramesh Nair",
            "type": "Monetary (Recurring)",
            "amount": "₹2,000/month",
            "campaign": "Emergency Medical Fund",
            "message": "",
            "anonymous": False
        },
        {
            "donor": "Infosys Foundation",
            "type": "Corporate CSR",
            "amount": "₹2,00,000",
            "campaign": "Build a Rural School",
            "message": "Funds to support school construction and furniture.",
            "anonymous": False
        },
        {
            "donor": "Ritu Verma",
            "type": "Monetary",
            "amount": "₹5,500",
            "campaign": "Shelter for the Homeless",
            "message": "For temporary beds during the rainy season.",
            "anonymous": False
        },
    ]
    return render(request, "donations_list.html", {"donations": donations})


@login_required
def education_view(request):
    campaigns = Campaign.objects.filter(category='education')
    return render(request, 'education.html', {'campaigns': campaigns})

@login_required
def food_view(request):
    campaigns = Campaign.objects.filter(category='food')
    return render(request, 'food.html', {'campaigns': campaigns})

@login_required
def clothes_view(request):
    campaigns = Campaign.objects.filter(category='clothes')
    return render(request, 'clothes.html', {'campaigns': campaigns})

@login_required
def medical_view(request):
    campaigns = Campaign.objects.filter(category='medical')
    return render(request, 'medical.html', {'campaigns': campaigns})

@login_required
def infrastructure_view(request):
    campaigns = Campaign.objects.filter(category='infrastructure')
    return render(request, 'infrastructure.html', {'campaigns': campaigns})

@login_required
def shelter_view(request):
    campaigns = Campaign.objects.filter(category='shelter')
    return render(request, 'shelter.html', {'campaigns': campaigns})

@login_required
def donation_view(request, campaign_id):
    if campaign_id:
        campaign = get_object_or_404(Campaign, id=campaign_id)
    else:
        campaign = None
    try:
        profile = Profile.objects.get(user=request.user)
        phone_number = profile.phone
    except Profile.DoesNotExist:
        phone_number = ''
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user = request.user  # ✅ Ensure user is saved if your Donation model has user field
            donation.save()
            return render(request, 'thankyou.html', {'donation': donation})  # ✅ Show thankyou.html
    else:
        form = DonationForm(initial={'campaign': campaign,
            'name': request.user.username,
            'email': request.user.email,
            'phone': phone_number,   
            'purpose': campaign.description,             
            })

    return render(request, 'donate.html', {'form': form, 'campaign': campaign})

@login_required
def thankyou(request):
    return render(request,'thankyou.html')

@login_required
def approved_donations(request):
    donations = Donation.objects.filter(is_approved=True, is_rejected=False)
    return render(request, 'approved_list.html', {'donations': donations})

@login_required
def contact_admin(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user  # Attach logged-in user
            contact.name = request.user.first_name or request.user.username
            contact.email = request.user.email
            contact.save()

            messages.success(request, 'Your message has been sent to the admin.')
            return redirect('contact_admin')
    else:
        form = ContactForm()

    return render(request, 'contact_admin.html', {
        'form': form,
        'user_name': request.user.first_name or request.user.username,
        'user_email': request.user.email,
    })

@staff_member_required
def view_queries(request):
    queries = ContactQuery.objects.all().order_by('-sent_at')
    return render(request, 'view_queries.html', {'queries': queries})

@staff_member_required
def reply_to_query(request, query_id):
    query = get_object_or_404(ContactQuery, id=query_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipient_email = query.email

            # Sending email
            send_mail(
                subject,
                message,
                request.user.email,  # Admin's email as sender
                [recipient_email],
                fail_silently=False,
            )

            messages.success(request, 'Reply sent successfully.')
            return redirect('view_queries')
    else:
        form = ReplyForm(initial={'subject': f"Re: {query.subject}"})

    return render(request, 'reply_to_query.html', {'form': form, 'query': query})
@staff_member_required
def admin_approval_panel(request):
    donations = Donation.objects.filter(is_approved=False, is_rejected=False)
    return render(request, 'admin_approval_panel.html', {'donations': donations})

@login_required
def request_assistance(request):
    if request.method == 'POST':
        form = RecipientRequestForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, "Request submitted. Awaiting admin verification.")
            return redirect('dashboard')
    else:
        form = RecipientRequestForm()

    return render(request, 'recipient_request_form.html', {'form': form})

# ✅ Approve Donation
@staff_member_required
def approve_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    donation.is_approved = True
    donation.is_rejected = False
    donation.save()
    if donation.amount:
            campaign = donation.campaign
            campaign.collected_amount += Decimal(donation.amount)
            campaign.save()
    send_mail(
        'Donation Approved ✅',
        f'Dear {donation.name},\n\nThank you for your generous donation towards {donation.campaign.title}. Your donation has been approved.\n\nRegards,\nDonations Team',
        settings.EMAIL_HOST_USER,
        [donation.email],
        fail_silently=False,
    )
    return redirect('admin_approval_panel')

# ✅ Reject Donation
@staff_member_required
def reject_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    donation.is_approved = False
    donation.is_rejected = True
    donation.save()

    # ✅ Send rejection mail
    send_mail(
        'Donation Rejected ❌',
        f'Dear {donation.name},\n\nUnfortunately, your donation towards {donation.campaign.title} has been rejected. For any queries, please contact us.\n\nRegards,\nDonations Team',
        settings.EMAIL_HOST_USER,
        [donation.email],
        fail_silently=False,
    )

    return redirect('admin_approval_panel')


@login_required
def recipient_request_form(request):
    if request.method == 'POST':
        form = RecipientRequestForm(request.POST, request.FILES)
        if form.is_valid():
            recipient_request = form.save(commit=False)
            recipient_request.user = request.user
            recipient_request.save()
            return redirect('dashboard')  # or any success page
    else:
        form = RecipientRequestForm()
    
    return render(request, 'recipient_request_form.html', {'form': form})

@staff_member_required
def admin_recipient_requests(request):
    requests = RecipientRequest.objects.all()
    return render(request, 'admin_recipient_requests.html', {'requests': requests})

@staff_member_required
def approve_recipient_request(request, request_id):
    req = get_object_or_404(RecipientRequest, id=request_id)
    req.is_approved = True
    req.is_rejected = False
    req.save()
    send_mail(
        'Request Approved',
        'Your request has been approved by the admin.',
        settings.DEFAULT_FROM_EMAIL,
        [req.user.email],
        fail_silently=False
    )
    messages.success(request, "Request approved and user notified.")
    return redirect('admin_recipient_requests')


@staff_member_required
def reject_recipient_request(request, request_id):
    req = get_object_or_404(RecipientRequest, id=request_id)
    req.is_approved = False
    req.is_rejected = True
    req.save()
    send_mail(
        'Request Rejected',
        'Your request has been rejected by the admin.',
        settings.DEFAULT_FROM_EMAIL,
        [req.user.email],
        fail_silently=False
    )
    messages.error(request, "Request rejected and user notified.")
    return redirect('admin_recipient_requests')


@login_required
def my_request_status(request):
    my_requests = RecipientRequest.objects.filter(user=request.user).order_by('-created_at')  # latest first
    return render(request, 'recipient_request_status.html', {'my_requests': my_requests})
