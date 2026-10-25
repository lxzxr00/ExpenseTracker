import flet as ft
import views.user
from views.user import user_account, current_user


def build_add_groups_view(page: ft.Page):

    groups_field = ft.TextField()

    def add_groups_clicked():
        user_account.add_groups(current_user, groups_field)
        page.navigate("/core")

    def go_back():
        page.navigate("/core")
    return ft.View(
                route = "/add_groups",
                controls = [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                                ft.Container(
                                    content=ft.Text(
                                        "Enter Group Name : ",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                        font_family="ROBOTO",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    width=float("inf"),
                                    padding=ft.Padding(0, 50, 0, 50),
                                ),
                                
                                ft.Container(groups_field, alignment = ft.Alignment( 0, 0),),
                                ft.FilledButton(content=ft.Text("Add Groups"), on_click=add_groups_clicked)
                                
                            ]
                        )
                    )
        
                ],
            )