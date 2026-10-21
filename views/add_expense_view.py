import flet as ft
import views.user
from views.user import user_account


def build_add_expense_view(page: ft.Page):

    label_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)
    expense_field = ft.TextField(keyboard_type = ft.KeyboardType.TEXT)

    return ft.View(
            route = "/add_expense",
            controls = [
                ft.SafeArea(
                    ft.Column(
                        [
                            
                            ft.Text("Label : "),
                            ft.Container(label_field, alignment = ft.Alignment( 0, 0),),
                            ft.Text("Description : "),
                            ft.Container(expense_field, alignment = ft.Alignment( 0, 0),),
                            
                        ]
                    )
                )
    
            ],
        )