import flet as ft
import views.user
import os

# Signup View Screen / Create an Account Screen

def build_signup_view(page: ft.Page):

    email_field = ft.TextField(keyboard_type= ft.KeyboardType.TEXT)
    password_field = ft.TextField(keyboard_type= ft.KeyboardType.TEXT,
                                  password = True)
    confirm_password_field = ft.TextField(keyboard_type= ft.KeyboardType.TEXT,
                                          password = True)

    def send_create_request(e):
        print("email_field = ", email_field.value)
        print("password_field = ", password_field.value)
        print("confirm_password_field = ", confirm_password_field.value)

        if password_field.value == confirm_password_field.value:
            print("Your passwords match")
            # Here we are creating the object that is going to be saved in our document
            account = views.user.user_account()
            account.create_account(email_field.value, password_field.value)

            page.navigate("/login")
        else:
            print("Your passwords do not match")

    return ft.View(
        route = "/signup",
        controls = [
            ft.SafeArea(
                ft.Column(
                    [
                        ft.Container(
                            content = ft.Text(
                                "Create an account",
                                size = 25,
                                weight = ft.FontWeight.BOLD,
                                font_family = "Roboto",
                            ),
                            alignment = ft.Alignment( 0, 0),
                            width = float("inf"),
                            padding = ft.Padding( 0, 50, 0, 50),
                        ),
                        ft.Text("Email : "),
                        ft.Container(email_field, alignment = ft.Alignment( 0, 0),),
                        ft.Text("Password : "),
                        ft.Container(password_field, alignment = ft.Alignment( 0, 0),),
                        ft.Text("Confirm password : "),
                        ft.Container(confirm_password_field, alignment = ft.Alignment( 0, 0),),
                        ft.FilledButton(content=ft.Text("Create an account"), on_click=send_create_request),
                        ft.FilledButton(content=ft.Text("Back to Login"), on_click=lambda e: page.navigate("/login")),
                    ]
                )
            )
        ]
    )