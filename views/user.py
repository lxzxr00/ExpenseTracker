from db import supabase

# We're going to use this file to store our very important user variables
# For now, we're not going to be concerned with hashing the string values
# We will start with simply storing the files within a text document

# Each username will have their own file, the name of the text document inside
# will also be their username, the contents of the text document will be their password

# User data will eventually have to migrate to a database, so we should make sure the
# hashing is set up properly before we migrate the system

class user_account:
    def __init__(self):
        self.email = ""
        self.user_id = None
        self.is_logged_in = False

    def create_account(self, email, password):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            print("Successfully created account")
            return True
        except Exception as err:
            print("Sign up failed: ", err)
            return False

    def login(self, email, password):
        try:
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            self.is_logged_in = True
            self.email = response.user.email
            print("Successfully logged in")
            return True
        except Exception as err:
            print("Login failed: ", err)
            return False

    def logout(self):
        supabase.auth.sign_out()
        self.is_logged_in = False
        self.email = ""
        self.user_id = None

    def get_username(self):
        return self.email.split("@")[0]

    def add_expense(self, label, expense):
        pass

current_user=user_account()
