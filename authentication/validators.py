import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

""" 
If Default Auth Validations are not sufficient then we can Create Our Own Validator
refer: https://docs.djangoproject.com/en/4.0/topics/auth/passwords/#password-validation
"""

class SpecialcharValidator(object):
    """
    This will Handle Password should have at least 1 Special character
    this method will work on Regex special chars
    """

    def validate(self, password, user=None):
        if not re.search("[@_!#$%^&*()<>?/\|}{~:)]",password):
            raise ValidationError(
                _("The password must contain at least 1 Special Character."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "The password must contain at least 1 Special Character."
        )


class NumericValidator(object):
    """
    This will Handle Password should not contain only Numeric Value
    """
    def validate(self, password, user=None):
        if not re.findall('[0-9]', password):
            raise ValidationError(
                _("The password must contain at least 1 numeric, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 numeric letter, A-Z."
        )


class UppercaseValidator(object):
    """
    This will Handle Password should have at least 1 Uppercase letter
    this method will work on Regex Upper Case letters
    """
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class LowercaseValidator(object):
    """
    This will Handle Password should have at least 1 Lowercase letter
    this method will work on Regex Lower Case letters
    """
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase letter, a-z."
        )
