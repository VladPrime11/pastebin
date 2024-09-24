from django.contrib.auth.hashers import make_password, check_password


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password before saving it to the database."""
        return make_password(password)

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Checks the entered password with a hash."""
        return check_password(password, hashed_password)
