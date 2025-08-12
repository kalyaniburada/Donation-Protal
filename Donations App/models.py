from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
        ('admin', 'Admin')
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    address = models.TextField()

    def _str_(self):
        return self.user.username


class Campaign(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('food', 'Food'),
        ('clothes', 'Clothes'),
        ('medical', 'Medical'),
        ('infrastructure', 'Infrastructure'),
        ('shelter', 'Shelter'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='education'  # ✅ Default added to avoid migration prompt
    )

    def _str_(self):
        return self.title


class Donation(models.Model):
    DONATION_TYPE = (
        ('money', 'Money'),
        ('goods', 'Physical Items'),
    )
    donation_type = models.CharField(
        max_length=10,
        choices=DONATION_TYPE,
        default='money'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default='Anonymous')
    phone = models.CharField(max_length=15, default='Unknown')
    email = models.EmailField(default='test@example.com')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    purpose = models.TextField(default='General Donation')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00
    )
    address = models.TextField(null=True, blank=True, default='Not Provided')
    donated_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def _str_(self):
        return f"{self.name} - {self.donation_type}"


class ContactQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f'Message from {self.name}'


class Organization(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food Relief'),
        ('temple', 'Temples'),
        ('education', 'Education'),
        ('medical', 'Medical'),
        ('clothes', 'Clothing'),
        ('shelter', 'Shelter'),
        ('infrastructure', 'Infrastructure'),
    ]

    name = models.CharField(max_length=100)
    website_url = models.URLField()
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='temple'
    )
    image = models.ImageField(upload_to='organization_images/', blank=True, null=True)

    def _str_(self):
        return self.name


class RecipientRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    aadhaar_number = models.CharField(max_length=12, default='000000000000')
    ration_card_number = models.CharField(max_length=20, default='UNKNOWN')
    aadhaar_file = models.FileField(upload_to='aadhaar_files/', null=True, blank=True)
    ration_card_file = models.FileField(upload_to='ration_card_files/', null=True, blank=True)
    family_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.aadhaar_number}"