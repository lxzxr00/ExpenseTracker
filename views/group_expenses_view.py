import flet as ft
import views.user
from views.user import user_account, current_user

def build_group_expenses_view(page: ft.Page):
    groups_field = ft.TextField()

    def group_expenses_clicked():
        user_account.access_groups(current_user, groups_field)
        page.navigate("/core")

    def go_back():
        page.navigate("/core")
    return ft.View(
                route = "/group_expenses",
                controls = [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                                ft.Container(
                                    content=ft.Text(
                                        "Your Groups",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                        font_family="ROBOTO",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    width=float("inf"),
                                    padding=ft.Padding(0, 50, 0, 50),
                                ),
                                
                                
                                
                            ]
                        )
                    )
        
                ],
            )