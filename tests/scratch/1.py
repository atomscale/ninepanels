from passlib.context import CryptContext


hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return hash_context.hash(password)

print(get_password_hash("apponfleek6969"))