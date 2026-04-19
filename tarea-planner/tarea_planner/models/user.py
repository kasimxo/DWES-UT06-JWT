import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

"""
Voy a necesitar un alumno y un profesor
Necesitaré:
- Nombre completo
- Email
- Password
- Rol (alumno o profesor)

Como estas cosas son comunes para ambos, voy a hacer un solo modelo con una distinción de rol
"""
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
        )
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    ROLE_CHOICES = [
        ('student', 'Alumno'),
        ('teacher', 'Profesor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
