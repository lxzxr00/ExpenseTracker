import flet as ft
import views.user
from views.user import user_account, current_user

def build_transfer_funds_view(page: ft.Page):

    transfer_field = ft.TextField(keyboard_type = ft.KeyboardType.NUMBER)

    def transfer_clicked():
        user_account.transfer_funds(current_user, transfer_field)
        page.navigate("/core")

    def go_back():
        page.navigate("/core")
    return ft.View(
                route = "/transfer_funds",
                controls = [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                                ft.Container(
                                    content=ft.Text(
                                        "Transfer Funds : ",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                        font_family="ROBOTO",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    width=float("inf"),
                                    padding=ft.Padding(0, 50, 0, 50),
                                ),
                                
                                ft.Text("Amount : "),
                                ft.Container(transfer_field, alignment = ft.Alignment( 0, 0),),
                                ft.Text("User : "),
                                ft.Container(transfer_field, alignment = ft.Alignment( 0, 0),),
                                ft.FilledButton(content=ft.Text("Pay"), on_click=transfer_clicked),
                                ft.FilledButton(content=ft.Text("Request a Payment "), on_click=transfer_clicked)
                                
                            ]
                        )
                    )
        
                ],
            )