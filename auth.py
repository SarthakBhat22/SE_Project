import pickle 
from pathlib import Path

import streamlit_authenticator as stauth

names = ["User1", "Admin"]
usernames = ["user1", "admin"]
passwords = []

hashed_passwords = stauth.Hasher(passwords).generate()
filepath = Path(__file__).parent / "hashed.pkl"
with filepath.open("wb") as file:
    pickle.dump(hashed_passwords, file)