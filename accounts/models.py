from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from core.models import TimeStampedModel, Tenant

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email adresi zorunludur')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPERADMIN')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, TimeStampedModel):
    ROLE_CHOICES = [
        ('SUPERADMIN', 'Süper Admin'),
        ('ADMIN', 'Merkez Admin'),
        ('DEALER', 'Bayi'),
        ('STAFF', 'Personel'),
    ]
    
    username = None
    email = models.EmailField(unique=True, verbose_name="E-posta")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEALER', db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    
    dealer = models.OneToOneField('Dealer', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_account')
    fcm_token = models.TextField(blank=True, default='', verbose_name='FCM Cihaz Token')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
        
    @property
    def is_distributor(self):
        return self.role in ['SUPERADMIN', 'ADMIN']
        
    @property
    def is_dealer(self):
        return self.role == 'DEALER'

class Dealer(TimeStampedModel):
    """Bayi (Müşteri) modeli - Her bayi bir tenant'a bağlı"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='dealers')
    code = models.CharField(max_length=20, verbose_name="Bayi Kodu", db_index=True)
    name = models.CharField(max_length=255, verbose_name="Bayi Adı")
    tax_office = models.CharField(max_length=100, verbose_name="Vergi Dairesi")
    tax_number = models.CharField(max_length=20, verbose_name="Vergi No")
    
    address = models.TextField(verbose_name="Adres")
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    # Giriş için kullanılmaz — oturum yalnızca users.email ile açılır
    email = models.EmailField(blank=True, verbose_name="İletişim E-postası")
    
    is_active = models.BooleanField(default=True, db_index=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Kredi Limiti")
    payment_term_days = models.IntegerField(default=30, verbose_name="Vade Günü")
    
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="İskonto Oranı %")
    
    class Meta:
        db_table = 'dealers'
        verbose_name = 'Bayi'
        verbose_name_plural = 'Bayiler'
        unique_together = [['tenant', 'code']]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', 'code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_current_balance(self):
        """Bayinin güncel borç/alacak durumu"""
        from finance.models import CariAccount
        return CariAccount.objects.filter(dealer=self).aggregate(
            balance=models.Sum('amount')
        )['balance'] or 0
