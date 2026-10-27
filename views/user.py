from db import supabase
import random

# We're going to use this file to store our very important user variables
# For now, we're not going to be concerned with hashing the string values
# Supabase ended up handling hashing these values, will turn on RLS once the database is completely finished
# We will start with simply storing the files within a text document

# Each username will have their own file, the name of the text document inside
# will also be their username, the contents of the text document will be their password

# User data will eventually have to migrate to a database, so we should make sure the
# hashing is set up properly before we migrate the system

class user_account:
    def __init__(self):
        self.display_name = ""
        self.tag = ""
        self.email = ""
        self.user_id = None
        self.is_logged_in = False
        self.current_group = None

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
            self.user_id = response.user.id
            self.load_profile()
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
        self.display_name = ""
        self.tag = ""

    def get_username(self):
        if self.display_name:
            return f"{self.display_name}#{self.tag}"
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
                    .select("id, label, amount, created_at, category_id, contribution_id, categories(name, color)")
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

# We need to create profiles, so that these accounts can interact with one another =====================================

    def load_profile(self):
        try:
            response = (
                supabase.table("profiles")
                .select("display_name, tag")
                .eq("id", self.user_id)
                .execute()
            )
            if response.data:
                self.display_name = response.data[0]["display_name"]
                self.tag = response.data[0]["tag"]
                return True
        except Exception as err:
            print("Load profile failed: ", err)
            return False

    def has_profile(self):
        return bool(self.display_name)

    def create_profile(self, display_name):
        # We're gonna make tags based on userID, but if they return collisions, we'll use random ones
        base = int(self.user_id.replace("-", "")[:8], 16) % 10000
        for attempt in range(5):
            number = base if attempt == 0 else random.randint(0, 9999)
            tag = f"{number:04d}"
            try:
                supabase.table("profiles").insert(
                    {"id": self.user_id, "display_name": display_name, "tag": tag}
                ).execute()
                self.display_name = display_name
                self.tag = tag
                return True
            except Exception as err:
                if "duplicate" not in str(err).lower():
                    print("Could not create profile", err)
                    return False
        return False

    def search_profiles(self, query):
        query = query.strip()
        if not query:
            return []
        try:
            request = supabase.table("profiles").select("id, display_name, tag")
            if "#" in query:
                name, tag = query.split("#", 1)
                request = request.ilike("display_name", name.strip()).eq("tag", tag.strip())
            else:
                request = request.ilike("display_name", f"%{query}%")
            res = request.neq("id", self.user_id).limit(20).execute()
            return res.data
        except Exception as err:
            print("Search profile failed: ", err)
            return []

# Now we need to make the groups, this has already been added on supabase ==============================================

    def get_groups(self):
        try:
            response = (
                supabase.table("group_members")
                .select("status, groups(id, name, owner_id)")
                .eq("user_id", self.user_id)
                .execute()
            )
            return [row for row in response.data if row.get("groups")]
        except Exception as err:
            print("Could not load groups:", err)
            return []

    def create_group(self, name, invitee_ids):
        try:
            response = supabase.rpc(
                "create_group", {"group_name": name, "invitee_ids": invitee_ids}
            ).execute()
            return response.data
        except Exception as err:
            print("Could not create group:", err)
            return None

    def accept_invite(self, group_id):
        try:
            supabase.table("group_members").update({"status": "member"}).eq(
                "group_id", group_id
            ).eq("user_id", self.user_id).execute()
            return True
        except Exception as err:
            print("Could not accept invite:", err)
            return False

    def decline_invite(self, group_id):
        try:
            supabase.table("group_members").delete().eq("group_id", group_id).eq(
                "user_id", self.user_id
            ).execute()
            return True
        except Exception as err:
            print("Could not decline invite:", err)
            return False

    # We Need these for the next portion, which will be the group view and member contributions ========================
    def get_group_members(self, group_id):
        try:
            response = (
                supabase.table("group_members")
                .select("user_id, status, profiles!group_members_user_id_fkey(display_name, tag)")
                .eq("group_id", group_id)
                .order("created_at")
                .execute()
            )
            return response.data
        except Exception as err:
            print("Could not load members:", err)
            return []

    def get_group_payments(self, group_id):
        try:
            response = (
                supabase.table("group_payments")
                .select(
                    "id, title, amount, created_at, "
                    "creator:profiles(display_name, tag), "
                    "group_contributions(user_id, amount, profiles(display_name, tag))"
                )
                .eq("group_id", group_id)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as err:
            print("Could not load payments:", err)
            return []

    def post_group_payment(self, group_id, title, amount):
        try:
            supabase.table("group_payments").insert(
                {"group_id": group_id, "title": title, "amount": amount}
            ).execute()
            return True
        except Exception as err:
            print("Could not post payment:", err)
            return False

    def contribute(self, payment_id, amount):
        try:
            supabase.rpc(
                "contribute_to_payment",
                {"p_payment_id": payment_id, "p_amount": amount},
            ).execute()
            return True, ""
        except Exception as err:
            print("Could not contribute:", err)
            return False, getattr(err, "message", str(err))

    # Forgot to make a delete group function, so those functions go here ===============================================
    def leave_group(self, group_id):
        try:
            response = supabase.rpc("leave_group", {"p_group_id": group_id}).execute()
            # left/transferred/deleted
            return response.data
        except Exception as err:
            print("Could not leave group:", err)
            return None

    def delete_group(self, group_id):
        try:
            supabase.table("groups").delete().eq("id", group_id).execute()
            return True
        except Exception as err:
            print("Could not delete group:", err)
            return False

    # Sections needed for Transfers ====================================================================================

    def get_transfers(self):
        try:
            response = (
                supabase.table("transfers")
                .select(
                    "id, from_user, to_user, amount, note, kind, status, "
                    "initiated_by, dismissed, created_at, "
                    "payer:profiles!transfers_from_user_fkey(id, display_name, tag), "
                    "payee:profiles!transfers_to_user_fkey(id, display_name, tag)"
                )
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            return response.data
        except Exception as err:
            print("Could not load transfers:", err)
            return []

    def _call(self, function_name, params):
        try:
            supabase.rpc(function_name, params).execute()
            return True, ""
        except Exception as err:
            print(f"{function_name} failed:", err)
            return False, getattr(err, "message", str(err))

    def send_money(self, to_id, amount, note):
        return self._call("send_money", {"p_to": to_id, "p_amount": amount, "p_note": note})

    def request_money(self, from_id, amount, note):
        return self._call("request_money", {"p_from": from_id, "p_amount": amount, "p_note": note})

    def pay_request(self, transfer_id):
        return self._call("pay_request", {"p_id": transfer_id})

    def decline_request(self, transfer_id):
        return self._call("decline_request", {"p_id": transfer_id})

    def cancel_request(self, transfer_id):
        return self._call("cancel_request", {"p_id": transfer_id})

    def dismiss_transfer(self, transfer_id):
        return self._call("dismiss_transfer", {"p_id": transfer_id})

    # Summary section use case functions ===============================================================================
    def get_expenses_since(self, start_iso):
        try:
            response = (
                supabase.table("expenses")
                .select("id, label, amount, created_at, category_id")
                .gte("created_at", start_iso)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as err:
            print("Could not load expenses:", err)
            return []

# Creating the user object corresponding to the email+password
current_user=user_account()
