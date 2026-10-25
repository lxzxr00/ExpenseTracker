import flet as ft
import views.user
from views.user import user_account, current_user

def build_summary_view(page: ft.Page):

    summary_field = ft.TextField(keyboard_type = ft.KeyboardType.NUMBER)

    def summary_clicked():
        user_account.summary(current_user, summary_field)
        page.navigate("/core")

    def go_back():
        page.navigate("/core")
    return ft.View(
                route = "/summary",
                controls = [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                                ft.Container(
                                    content=ft.Text(
                                        "Summary",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                        font_family="ROBOTO",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    width=float("inf"),
                                    padding=ft.Padding(0, 50, 0, 50),
                                ),
                                ft.Text("Enter Time period: "),
                                ft.Container(summary_field, alignment = ft.Alignment( 0, 0),),
                                ft.FilledButton(content=ft.Text("Result"), on_click=summary_clicked)
                                
                            ]
                        )
                    )
        
                ],
            )