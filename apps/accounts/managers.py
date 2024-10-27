# manager.py

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Please enter a valid email address"))


    def create_user(self, email, first_name, last_name, password, **extra_fields):
        if not email:
            raise ValueError(_("An email address is required"))
        email = self.normalize_email(email)
        self.email_validator(email)

        if not first_name:
            raise ValidationError(_("first name is required"))
        if not last_name:
            raise ValidationError(_("last name is required"))

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("is_staff must be True for admin user"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("is_superuser must be True for admin user"))
        return self.create_user(email, first_name, last_name, password, **extra_fields)
