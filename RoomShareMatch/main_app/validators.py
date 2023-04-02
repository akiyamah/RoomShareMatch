from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UpperCaseAndLowerCaseValidator:
    def validate(self, password, user=None):
        if not (any(c.islower() for c in password) and any(c.isupper() for c in password)):
            raise ValidationError(
                _("パスワードは少なくとも1つの大文字英字と1つの小文字英字を含む必要があります。"),
                code='password_no_upper_and_lower',
            )

    def get_help_text(self):
        return _("パスワードは少なくとも1つの大文字英字と1つの小文字英字を含む必要があります。")
