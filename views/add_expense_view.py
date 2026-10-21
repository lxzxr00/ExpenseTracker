import flet as ft
import views.user
from views.user import user_account, current_user


def build_add_expense_view(page: ft.Page):

    label_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)
    expense_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)

    def add_expense_clicked():
        user_account.add_expense(current_user, label_field, expense_field)
        page.navigate("/core")

    def go_back():
        page.navigate("/core")

    return ft.View(
            route = "/add_expense",
            controls = [
                ft.SafeArea(
                    ft.Column(
                        [
                            ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                            ft.Container(
                                content=ft.Text(
                                    "New Expense : ",
                                    size=25,
                                    weight=ft.FontWeight.BOLD,
                                    font_family="ROBOTO",
                                ),
                                alignment=ft.Alignment(0, 0),
                                width=float("inf"),
                                padding=ft.Padding(0, 50, 0, 50),
                            ),
                            ft.Text("Label  : "),
                            ft.Container(label_field, alignment = ft.Alignment( 0, 0),),
                            ft.Text("Amount : "),
                            ft.Container(expense_field, alignment = ft.Alignment( 0, 0),),
                            ft.FilledButton(content=ft.Text("Add Expense"), on_click=add_expense_clicked)

                            
                        ]
                    )
                )
    
            ],
        )