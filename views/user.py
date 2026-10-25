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

    def add_expense(self, label, amount, category_id=None):
        try:
            supabase.table("expenses").insert(
                {"label": label, "amount": amount, "category_id": category_id}
            ).execute()
            return True
        except Exception as err:
            print("Add expense failed: ", err)
            return False

    def delete_expense(self, expense_id):
        try:
            supabase.table("expenses").delete().eq("id", expense_id).execute()
            return True
        except Exception as err:
            print("Delete expense failed: ", err)
            return False

    def get_expenses(self):
        try:
            response = (
                supabase.table("expenses")
                    .select("id, label, amount, created_at, category_id, categories(name, color)")
                    .order("created_at", desc=True)
                    .execute()
                    )
            return response.data
        except Exception as err:
            print("Get expenses failed: ", err)
            return []

    def update_expense(self, expense_id, label, amount, category_id):
        try:
            supabase.table("expenses").update(
                {"label": label, "amount": amount, "category_id": category_id}
            ).eq("id", expense_id).execute()
            return True
        except Exception as err:
            print("Update expense failed: ", err)
            return False

# Below is for the budget view =========================================================================================

    def get_categories(self):
        try:
            response = (
                supabase.table("categories")
                .select("id, name, color, budget")
                .order("name")
                .execute()
            )
            return response.data
        except Exception as err:
            print("Could not load categories: ", err)
            return []


    def add_category(self, name, color, budget):
        try:
            supabase.table("categories").insert(
                {"name": name, "color": color, "budget": budget}
            ).execute()
            return True
        except Exception as err:
            print("Could not add Category: ", err)
            return False

    def update_category(self, id, name, color, budget):
        try:
            supabase.table("categories").update(
                {"name": name, "color": color, "budget": budget}
            ).eq("id", id).execute()
            return True
        except Exception as err:
            print("Could not update Category: ", err)
            return False

    def delete_category(self, id):
        try:
            supabase.table("categories").delete().eq("id", id).execute()
            return True
        except Exception as err:
            print("Could not delete Category: ", err)
            return False


# Creating the user object corresponding to the email+password
current_user=user_account()
