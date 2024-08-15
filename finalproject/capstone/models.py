from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission



#this is for user registration model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='Customer'):
        if not email:
            raise ValueError('Users must have an email address')
        
        # ensure that the email is case-insensitive
        email = self.normalize_email(email)
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            role=role,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password, role='Administrator'):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            password=password,
            role='Administrator',
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('Administrator', 'Administrator'),
        ('Customer', 'Customer'),
    )

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLES, default='Customer')
    #meters = models.ManyToManyField('Meter', blank=True, related_name='assigned_users')
    #product_id = models.ForeignKey(Meter, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='customuser_set',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='customuser_set',
        related_query_name='user'
    )
    

    def __str__(self):
        return self.email

# this is for storing the product id, name and location of the mete
class Meter(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length = 255)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='meters')
    last_alert_timestamp = models.DateTimeField(null=True, blank=True)
     
    def __str__(self):
        return self.name
   
#this stores the sensor data values 
class SensorData(models.Model):
    sensor_data_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Meter, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    voltage =models.FloatField()
    current =models.FloatField()
    power =models.FloatField()
    energy =models.FloatField()
    kVA = models.FloatField(default=0)
    power_factor = models.FloatField(default=0)
    billing = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    alert_sent = models.BooleanField(default=False)
    def __str__(self):
        return f"SensorData({self.product_id},{self.timestamp})"

    