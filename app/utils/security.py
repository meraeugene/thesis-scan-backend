from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    max_len = 72
    password_trunc = password[:max_len]
    print("Password value:", repr(password_trunc), "Length (chars):", len(password_trunc))
    return pwd_context.hash(password_trunc)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
