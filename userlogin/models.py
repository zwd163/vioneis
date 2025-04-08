from django.db import models
from django.utils import timezone
import uuid

class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens
    """
    user_id = models.IntegerField(verbose_name="User ID")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Reset Token")
    email = models.EmailField(verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    expires_at = models.DateTimeField(verbose_name="Expires At")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")

    def __str__(self):
        return f"Reset token for user {self.user_id}"

    def is_valid(self):
        """Check if the token is valid (not expired and not used)"""
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def create_token(cls, user_id, email, expiry_hours=24):
        """Create a new password reset token"""
        expires_at = timezone.now() + timezone.timedelta(hours=expiry_hours)
        return cls.objects.create(
            user_id=user_id,
            email=email,
            expires_at=expires_at
        )