from pwdlib import PasswordHash
import argparse
from getpass import getpass
from database import create_db_and_tables, engine
from sqlmodel import SQLModel, Session
import crud
from models import UserRole

if __name__ == "__main__":
    password_hasher = PasswordHash.recommended()
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", nargs="?")
    args = parser.parse_args()
    username = args.username
    if username is None :
        username = input("What is your username : ")
    username=username.strip()
    password1 = getpass(prompt="password: ")
    password2 = getpass(prompt="reenter your password for confirmation: ")

    if password1!=password2 :
        raise ValueError("password is not the same")

    create_db_and_tables()
    with Session(engine) as session:
        try:
            crud.create_user(session, username, password_hasher.hash(password1), UserRole.ADMIN )
            print(f"Admin '{username}' created with success.")
        except ValueError as e:
            print(e) 
        