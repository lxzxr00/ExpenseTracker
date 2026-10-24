import flet as ft
import views.user
from views.user import user_account


# Login View Screen

def build_login_view(page: ft.Page):

    email_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)
    password_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT,
                                  password = True)

    def login_clicked(e):
        if email_field.value == "" or password_field.value == "":
            print("username or password field is empty")
            return
        print("Email entered : ", email_field.value)
        print("Password entered : ", password_field.value)
        views.user.current_user.login(email_field.value, password_field.value)
        if views.user.current_user.is_logged_in:
            print("Logged in")
            page.navigate("/core")
        else:
            print("Login failed")

    def create_account(e):
        page.navigate("/signup")

    return ft.View(
        route = "/login",
        controls = [
            ft.SafeArea(
                ft.Column(
                    [
                        ft.Container(
                            content = ft.Text(
                                "Expense Tracker V1",
                                size = 25,
                                weight = ft.FontWeight.BOLD,
                                font_family = "ROBOTO",
                            ),
                            alignment = ft.Alignment( 0, 0),
                            width = float("inf"),
                            padding = ft.Padding( 0, 50, 0, 50),
                        ),
                        ft.Text("Email : "),
                        ft.Container(email_field, alignment = ft.Alignment( 0, 0),),
                        ft.Text("Password : "),
                        ft.Container(password_field, alignment = ft.Alignment( 0, 0),),
                        ft.FilledButton(content = ft.Text(" Log in "), on_click = login_clicked),
                        ft.FilledButton(content = ft.Text("Sign up"), on_click = create_account)
                    ]
                )
            )

        ],
    )