"""Create one Admin account locally: `python -m app.admin_cli EMAIL`."""

import argparse
import getpass

from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal
from app.security import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Buat akun Admin CERNO secara administratif.")
    parser.add_argument("email")
    args = parser.parse_args()
    password = getpass.getpass("Kata sandi Admin (minimal 12 karakter): ")
    if len(password) < 12:
        raise SystemExit("Kata sandi terlalu pendek.")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == args.email.strip().lower())):
            raise SystemExit("Akun sudah ada; perintah ini tidak mengubah peran akun yang ada.")
        db.add(User(email=args.email.strip().lower(), password_hash=hash_password(password), role="admin"))
        db.commit()
    print("Akun Admin dibuat.")


if __name__ == "__main__":
    main()
