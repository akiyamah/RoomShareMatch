from django.core.exceptions import ValidationError
from django.utils.translation import gettext

class CustomPasswordValidator:
    '''
    CustomPasswordValidatorは補足の内容に含まれるフレームワーク以外に追加で確認するカスタムバリデータ。
    パスワードに以下の条件を満たすことを追加する。
    1. 少なくとも1つの大文字英字が含まれる。
    2. 少なくとも1つの小文字英字が含まれる。
    3. 少なくとも1つの数字または記号が含まれる。
    
    補足:
        UserCreationFormで実施ているバリテーション。
        1. パスワードの一致確認:
            clean_password2 メソッドでは、入力された二つのパスワード（password1 と password2）が一致していることを確認。
        2. パスワードバリデーション: 
            _post_clean メソッドでは、password_validation.validate_password を使って、
            入力されたパスワードが設定されたパスワードポリシー（長さ、複雑さなど）に従っているかを検証しています。
        password_validation.validate_password の詳細:
            MinimumLengthValidator: パスワードが最低限の長さ（デフォルトでは8文字）を持っていることを検証します。
            UserAttributeSimilarityValidator: パスワードがユーザー属性（ユーザ名やメールアドレスなど）とあまりに類似していないことを検証します。
            CommonPasswordValidator: パスワードが一般的に使われるパスワードでないことを検証します。
            NumericPasswordValidator: パスワードがすべて数字で構成されていないことを検証します。
        3. ユーザ名のバリデーション: 
            ユーザ名に関しては、モデルのフィールド定義で指定されたバリデーションが適用されます。
            例えば、User モデルの username フィールドに unique=True が設定されている場合、同じユーザ名を持つユーザーが既に存在しないかを確認します。
    '''
    def validate(self, password, user=None):
        if not any(c.islower() for c in password):
            # c (character)に一つも小文字英字が含まれていない場合エラー。
            raise ValidationError(
                gettext("パスワードは少なくとも1つの小文字英字を含む必要があります。"),
                code='password_no_lower_case',
            )
        if not any(c.isupper() for c in password):
            raise ValidationError(
                gettext("パスワードは少なくとも1つの大文字英字を含む必要があります。"),
                code='password_no_upper_case',
            )
        if not any(c.isdigit() or c in '!@#$%^&*()-_=+[{]};:",<.>/?|`~' for c in password):
            raise ValidationError(
                gettext("パスワードは少なくとも1つの数字または記号を含む必要があります。"),
                code='password_no_digit_or_symbol',
            )
            
    def get_help_text(self):
        return gettext("パスワードは、1つの大文字英字、1つの小文字英字、および1つの数字または記号をすべて含む必要があります。")
