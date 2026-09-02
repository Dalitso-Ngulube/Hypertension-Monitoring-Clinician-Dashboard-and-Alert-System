import re

from django.core.exceptions import ValidationError


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'Password must contain at least one special character.',
                code='password_no_special'
            )

    def get_help_text(self):
        return 'Your password must contain at least one special character.'