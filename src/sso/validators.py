import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class UppercaseValidator(object):
    """The password must contain at least 1 uppercase letter, A-Z."""

    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter, A-Z.")


class LowercaseValidator(object):
    """The password must contain at least 1 lowercase letter, a-z."""

    def validate(self, password, user=None):
        if not re.findall("[a-z]", password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 lowercase letter, a-z.")


class SpecialCharValidator(object):
    """The password must contain at least 1 special character @#$%!^&*"""

    def validate(self, password, user=None):
        if not re.findall("[@#$%!^&*]", password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 special character: "
                    + "@#$%!^&*"
                ),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 special character: " + "@#$%!^&*"
        )


class NumberValidator(object):
    """The password must contain at least 1 number, 0-9."""

    def validate(self, password, user=None):
        if not re.findall("[0-9]", password):
            raise ValidationError(
                _("The password must contain at least 1 number, 0-9."),
                code="password_no_number",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 number, 0-9.")


class MaximumLengthValidator:
    """The password cannot be more than max_length characters."""

    def __init__(self, max_length=128):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _(
                    "This password is greater than the maximum of %(max_length)d characters."
                ),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password can be a maximum of %(max_length)d characters."
            % {"max_length": self.max_length}
        )
