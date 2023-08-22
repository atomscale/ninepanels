from passlib.context import CryptContext

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password) -> bool:
    return hash_context.verify(
        plain_password, hashed_password
    )  # returns a bool of match/no match


def get_password_hash(password):
    return hash_context.hash(password)

print(get_password_hash("newpassword"))