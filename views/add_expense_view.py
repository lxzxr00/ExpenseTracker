import flet as ft
from flet import KeyboardType

import views.user
from views.user import user_account, current_user
from views.widgets import category_dropdown, selected_category_id



def build_add_expense_view(page: ft.Page):
    user = views.user.current_user
    categories = user.get_categories()

    label_field = ft.TextField(label="Label")
    amount_field = ft.TextField(label="Amount", keyboard_type=KeyboardType.NUMBER)
    category_field = category_dropdown(categories)

    def add_expense_clicked():
        label_field.error_text = None
        amount_field.error_text = None

        label = str(label_field.value or "").strip()
        if not label:
            label_field.error_text = "Required"
            page.update()
            return

        try:
            amount = float(str(amount_field.value or "").strip())
        except ValueError:
            amount_field.error_text = "Invalid amount"
            page.update()
            return

        # After you've called the value's to be saved, it takes you back to the core view
        if user.add_expense(label, amount, selected_category_id(category_field)):
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
                            label_field,
                            amount_field,
                            category_field,
                            ft.FilledButton(
                                content=ft.Text("Add Expense"),
                                on_click=add_expense_clicked,
                            ),
                        ],
                        spacing=16,
                    )
                )
    
            ],
        )