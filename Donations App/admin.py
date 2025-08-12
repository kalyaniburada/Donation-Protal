from django.contrib import admin
from django.core.mail import send_mail
from .models import Donation, Campaign, Profile,Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'website_url')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'campaign', 'donation_type', 'amount', 'is_approved', 'is_rejected')
    list_filter = ('donation_type', 'is_approved', 'is_rejected')
    actions = ['approve_donations', 'reject_donations']

    def approve_donations(self, request, queryset):
        for donation in queryset:
            donation.is_approved = True
            donation.is_rejected = False
            donation.save()

            send_mail(
                subject='Donation Confirmation ✔️',
                message=f"Dear {donation.name},\n\nThank you for your donation of ₹{donation.amount} "
                        f"to '{donation.campaign.title}'. We appreciate your support.",
                from_email=None,
                recipient_list=[donation.email],
                fail_silently=False,
            )
        self.message_user(request, "Selected donations approved and emails sent ✅")

    def reject_donations(self, request, queryset):
        queryset.update(is_approved=False, is_rejected=True)
        self.message_user(request, "Selected donations rejected ❌")

    approve_donations.short_description = "✅ Approve selected donations & send email"
    reject_donations.short_description = "❌ Reject selected donations"


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'goal_amount', 'collected_amount', 'created_by')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'gender', 'address')
