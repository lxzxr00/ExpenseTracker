import flet as ft
import views.user


# Login View Screen

def build_login_view(page: ft.Page):
    user = views.user.current_user

    email_field = ft.TextField(
        label="Email",
        keyboard_type = ft.KeyboardType.EMAIL,
        autofocus= True,
    )

    password_field = ft.TextField(
        label="Password",
        can_reveal_password = True,
        password = True,
        on_submit=lambda e: login_clicked(e),
    )
    error_text = ft.Text(color=ft.Colors.ERROR, visible=False)

    def login_clicked(e):
        email_field.error_text = None
        password_field.error_text = None
        error_text.visible = False

        email = str(email_field.value or "").strip()
        password = str(password_field.value or "")

        if not email:
            email_field.error_text = "Required"
        if not password:
            password_field.error_text = "Required"
        if not email or not password:
            page.update()
            return

        if user.login(email, password):
            if user.has_profile():
                page.navigate("/core")
            else:
                page.navigate("/setup_profile")
        else:
            error_text.value = "Incorrect email or password"
            error_text.visible = True
            page.update()

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
                        email_field,
                        password_field,
                        error_text,
                        ft.FilledButton(content=ft.Text("Log in"), on_click=login_clicked),
                        ft.TextButton("Don't have an account? Sign up", on_click=create_account),
                    ],
                    spacing=16,
                )
            )

        ],
    )