from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with email as username field.
    first_name and last_name are inherited from AbstractUser.
    """

    username = None
    email = models.EmailField(_('email address'), unique=True)
    mobile = models.CharField(max_length=15)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20)  # 'student' or 'professional'
    is_email_verified = models.BooleanField(default=False)
    newsletter_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name if full_name.strip() else self.email


class Student(models.Model):
    """Student user profile"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    college_name = models.CharField(max_length=200)
    YEAR_CHOICES = (
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('5', '5th Year'),
    )
    year = models.CharField(max_length=10, choices=YEAR_CHOICES)
    branch = models.CharField(max_length=100)

    def __str__(self):
        return f"Student: {self.user.first_name} {self.user.last_name} ({self.user.email})"


class Professional(models.Model):
    """Professional user profile"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_profile')
    organization = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return f"Professional: {self.user.first_name} {self.user.last_name} ({self.user.email})"


class OTP(models.Model):
    """One-time password model for email verification"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.email}"
