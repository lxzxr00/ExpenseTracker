import flet as ft
import views.user
from views.user import user_account, current_user


def build_add_budget_view(page: ft.Page):

    budget_field = ft.TextField(keyboard_type = ft.KeyboardType.NUMBER)

    def add_budget_clicked():
        user_account.add_budget(current_user, budget_field)
        page.navigate("/core")

    def go_back():
        page.navigate("/core")
    return ft.View(
                route = "/add_budget",
                controls = [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                                ft.Container(
                                    content=ft.Text(
                                        "Enter Budget : ",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                        font_family="ROBOTO",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    width=float("inf"),
                                    padding=ft.Padding(0, 50, 0, 50),
                                ),
                                ft.Text("Amount : "),
                                ft.Container(budget_field, alignment = ft.Alignment( 0, 0),),
                                ft.FilledButton(content=ft.Text("Add Budget"), on_click=add_budget_clicked)
                                
                            ]
                        )
                    )
        
                ],
            )