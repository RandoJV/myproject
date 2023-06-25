from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, full_name=None, telephone_number=None, **extra_fields):
        """username ganti ke full name
        Create and save a user with the given email and password.
        if yg dibawah ditambah validasi no telp di bwah raise buat lagi 1 if buat phone number
        """
        if not email: 

            raise ValueError(_("The Email must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))
        if not full_name:
            raise ValueError(_("The Full Name must be set"))
        if not telephone_number:
            raise ValueError(_("The Phone must be set"))
        
        email = self.normalize_email(email)
        user = self.model(email=email,full_name=full_name,telephone_number=telephone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, full_name=None, telephone_number=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password,full_name, telephone_number, **extra_fields)