from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class UserProfileType(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    ORGANIZER = 'ORGANIZER', 'Organizer'
    PARTICIPANT = 'PARTICIPANT', 'Participant'


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('profile_type', UserProfileType.PARTICIPANT)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('profile_type', UserProfileType.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):

    id = models.AutoField(primary_key=True)
    email = models.EmailField(blank=True, default='', unique=True)
    name = models.CharField(max_length=255, blank=True, default='')

    phone_number = models.CharField(max_length=15, blank=True)
    profile_type = models.CharField(max_length=20, choices=UserProfileType.choices, default=UserProfileType.PARTICIPANT)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)


    #possible fields for ORGANIZERS
    cnpj_cpf = models.CharField(max_length=18, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    commercial_address = models.TextField(blank=True, null=True)


    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = []

    # related_name para evitar conflitos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name or self.email.split('@')[0]

    
    def clean(self):
        if self.profile_type == UserProfileType.PARTICIPANT:
            if self.is_staff or self.is_superuser:
                raise ValidationError("Participants can't be a staff or superuser.")
            
        if self.profile_type == UserProfileType.ADMIN:
            if not self.is_staff or not self.is_superuser:
                raise ValidationError("Administrators must be staff and superuser.")

                
        if self.profile_type == UserProfileType.ORGANIZER:
            if self.is_staff or self.is_superuser:
                raise ValidationError("Organizers can't be a staff or superuser.")
            if not self.cnpj_cpf:
                raise ValidationError("CNPJ/CPF is mandatory for organizers.")
            if not self.business_name:
                raise ValidationError("Business name is mandatory for organizers.")
            if not self.commercial_address:
                raise ValidationError("Commercial address is mandatory for organizers.")
            
    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)