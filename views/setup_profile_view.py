import re
import flet as ft
import views.user


def build_setup_profile_view(page: ft.Page):
    user = views.user.current_user
    name_field = ft.TextField(
        label="Display name",
        max_length=20,
    )

    def save_clicked(e):
        name = str(name_field.value or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", name):
            name_field.error_text = "Use 3–20 letters, numbers, or underscores"
            name_field.update()
            return
        if user.create_profile(name):
            page.navigate("/core")
        else:
            name_field.error_text = "Couldn't save that name. Try another."
            name_field.update()

    return ft.View(
        route="/setup_profile",
        controls=[
            ft.SafeArea(
                ft.Column(
                    [
                        ft.Text("Choose a display name", size=25, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "This is how other people will find you and see you in groups. "
                            "A # number is added automatically so names stay unique.",
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        name_field,
                        ft.FilledButton(content=ft.Text("Continue"), on_click=save_clicked),
                    ],
                    spacing=16,
                )
            )
        ],
    )