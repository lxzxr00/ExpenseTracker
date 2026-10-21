import os



# We're going to use this file to store our very important user variables
# For now, we're not going to be concerned with hashing the string values
# We will start with simply storing the files within a text document

# Each username will have their own file, the name of the text document inside
# will also be their username, the contents of the text document will be their password

# User data will eventually have to migrate to a database, so we should make sure the
# hashing is set up properly before we migrate the system

class user_account:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.is_logged_in = False

    def create_account(self, username, password):
        path = os.getcwd()
        os.mkdir(f'{path}/{username}')
        with open(f"{path}/{username}/{username}.txt", "w") as f:
            f.write(password)

    def check_if_exists(self, username):
        path = os.getcwd()
        return os.path.exists(f'{path}/{username}')

    def logout(self):
        self.is_logged_in = False

    def get_username(self):
        return self.username

    def login(self, username, password):
        path = os.getcwd()
        if self.check_if_exists(username):
            with open(f"{path}/{username}/{username}.txt", "r") as f:
                if password == f.read():
                    self.is_logged_in = True
                    self.username = username
                    print("Successfully logged in")
        else:
            print("Username does not exist")
            return

    def add_expense(self, label, expense):
        pass

current_user=user_account()
