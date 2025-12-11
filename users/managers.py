from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where identification is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(self, identification, username, email, password, **extra_fields):
        """
        Create and save a User with the given identification and password.
        """
        if not identification:
            msg = "The identification must be set"
            raise ValueError(msg)
        if not email:
            msg = "The email must be set"
            raise ValueError(msg)

        email = self.normalize_email(email)
        extra_fields.setdefault("is_verified", False)

        user = self.model(
            identification=identification, username=username, email=email, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identification, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given identification and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self.create_user(identification, username, email, password, **extra_fields)
