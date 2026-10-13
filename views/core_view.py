import flet as ft
import views.user
from views.user import user_account


# Main Menu Screen

def build_main_menu_view(page: ft.Page):

    def logout_clicked(e):
        pass


    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                padding=ft.Padding.only(left=28, top=20, bottom=12),
                content=ft.Text(
                    "Hello, <username>" , theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                ),
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                selected_icon=ft.Icons.NOTIFICATIONS,
                label="Create Groups",
                #on_click=function1,
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    async def handle_show_drawer(e):
        await page.show_drawer()


    return ft.View(
        route="/core",
        drawer= drawer,
        controls=[
        ft.SafeArea(
                ft.Column(
                    [
                        ft.Button(
                            "Show drawer",
                            icon=ft.Icons.MENU,
                            on_click=handle_show_drawer
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Expense Tracker V1",
                                size=25,
                                weight=ft.FontWeight.BOLD,
                                font_family="ROBOTO",
                            ),
                            alignment=ft.Alignment(0, 0),
                            width=float("inf"),
                            padding=ft.Padding(0, 50, 0, 50),
                        ),
                        ft.Text("You should be on you're main dashboard area"),
                        ft.FilledButton(content=ft.Text("temporary text"), on_click = logout_clicked)
                    ]
                )
            )
        ],
    )

