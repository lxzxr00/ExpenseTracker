import flet as ft
import views.user
from views.user import user_account, current_user

def build_settings_view(page: ft.Page):
    settings_field = ft.TextField(keyboard_type = ft.KeyboardType.NUMBER)

    def settings_clicked():
        user_account.settings(current_user, settings_field)
        page.navigate("/core")
    def go_back():
        page.navigate("/core")
    return ft.View(
        route="/settings",
        controls=[
            ft.SafeArea(
                ft.Column(
                    [
                        ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                        ft.Container(
                            content=ft.Text(
                                "Settings",
                                size=25,
                                weight=ft.FontWeight.BOLD,
                                font_family="ROBOTO",
                            ),
                            alignment=ft.Alignment(0, 0),
                            width=float("inf"),
                            padding=ft.Padding(0, 50, 0, 50),
                        ),
                        ft.Text("Settings : "),
                        ft.Container(settings_field, alignment = ft.Alignment( 0, 0),),
                        ft.FilledButton(content=ft.Text("Save"), on_click=settings_clicked)
                    ]
                )
            )
        ],
    )