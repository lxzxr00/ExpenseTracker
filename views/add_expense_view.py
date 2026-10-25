import flet as ft
import views.user
from views.user import user_account, current_user


def build_add_expense_view(page: ft.Page):

    label_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)
    amount_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)

    def add_expense_clicked():
        label = label_field.value.strip()
        try:
            amount = float(amount_field.value)
        except (TypeError, ValueError):
            print("Amount must be a number")
            return

        if not label:
            print("Label cannot be empty")
            return

        # After you've called the value's to be saved, it takes you back to the core view
        if views.user.current_user.add_expense(label, amount):
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
                            ft.Container(amount_field, alignment = ft.Alignment( 0, 0),),
                            ft.FilledButton(content=ft.Text("Add Expense"), on_click=add_expense_clicked)

                            
                        ]
                    )
                )
    
            ],
        )