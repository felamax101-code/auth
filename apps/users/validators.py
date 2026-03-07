
from django.core.validators import validate_email
#from django.contrib.auth import get_user_model
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

#User = get_user_model()
from.models import User


class EmailValidator:
    def __call__(self, email):
        # 1️⃣ Clean email
        email = email.strip().lower()

        # 2️⃣ Format check
        validate_email(email)

        # 3️⃣ Uniqueness check
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email already exists")

        # 4️⃣ Disposable domain check
        blocked_domains = {
            "tempmail.com",
            "mailinator.com",
            "10minutemail.com",
        }

        domain = email.split("@")[-1]
        if domain in blocked_domains:
            raise ValidationError("Disposable email addresses are not allowed")

        return email
    
    
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class StrongPasswordValidator:
    """
    Enforces:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """

    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code="password_no_uppercase",
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code="password_no_lowercase",
            )

        if not re.search(r"[0-9]", password):
            raise ValidationError(
                _("Password must contain at least one number."),
                code="password_no_number",
            )

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code="password_no_special",
            )
        common_passwords = ['password123', 'qwerty123', 'admin123', '12345678', 'welcome123']
        if value.lower() in common_passwords:
            raise serializers.ValidationError("This password is too common. Choose a stronger password.")

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )
        
        
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class FlexibleUsernameValidator:
    """
    A configurable username validator.

    Options:
    - allow_spaces
    - min_length
    - max_length
    - forbid_numeric_only
    - forbidden_usernames
    """

    def __init__(
        self,
        *,
        allow_spaces=True,
        min_length=2,
        max_length=150,
        forbid_numeric_only=True,
        forbidden_usernames=None,
        only_letters=True
    ):
        self.allow_spaces = allow_spaces
        self.min_length = min_length
        self.max_length = max_length
        self.forbid_numeric_only = forbid_numeric_only
        self.only_letters=only_letters
        self.forbidden_usernames = forbidden_usernames or {
            "admin", "root", "support", "system"
        }

    def __call__(self, username):
        username = username.strip()

        # Length
        if len(username) < self.min_length:
            raise ValidationError(
                _(f"Username must be at least {self.min_length} characters.")
            )

        if len(username) > self.max_length:
            raise ValidationError(
                _(f"Username must not exceed {self.max_length} characters.")
            )

        # Spaces
        if not self.allow_spaces and " " in username:
            raise ValidationError(_("Spaces are not allowed in username."))

        # Numeric only
        if self.forbid_numeric_only and username.replace(" ", "").isdigit():
            raise ValidationError(_("Username cannot be only numbers."))

        # Forbidden names
        if username.lower() in self.forbidden_usernames:
            raise ValidationError(_("This username is reserved."))
         # Only letters check
        if self.only_letters:
    
            username_to_check = username.replace(" ", "") if self.allow_spaces else username
    
    
            if not username_to_check.isalpha():
                raise ValidationError(_("Username must contain only letters.")) 
    
        

        return username


    