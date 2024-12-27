from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Worker ID field is required.")
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    avatar = models.ImageField(upload_to='profile_pics')
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ("Cashier", "Cashier"),
            ("Manager", "Manager"),
            ("Waiter", "Waiter"),
            ("IT Manager", "IT Manager"),
            ("General Manager", "General Manager"),
            ("Accountant", "Accountant"),
            ("CEO", "CEO"),
        ],
        blank=True,
        null=True,
    )
    level = models.IntegerField(
        default=1,
        choices=[
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
        ],
    )
    section = models.CharField(
        max_length=50,
        default="none",
        choices=[
            ("restaurant", "Restaurant"),
            ("arcade", "Arcade"),
            ("cosmetic_store", "Cosmetic Store"),
            ("salon", "Salon"),
            ("fashion", "Boutique"),
            ("spa", "Spa"),
            ("lounge", "Lounge"),
            ("all", "All"),
        ],
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Automatically generate Worker ID if it does not exist
        if not self.username:
            last_id = CustomUser.objects.order_by('id').last()
            next_id = last_id.id + 1 if last_id else 1
            self.username = f"{1000 + next_id}"  # Example: 1001, 1002, etc.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
