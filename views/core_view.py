import flet as ft
import views.user
from views.user import current_user

# Main Menu Screen

def build_main_menu_view(page: ft.Page):

    def logout_clicked(e):
        current_user.logout
        page.navigate("/login")

    def add_expense_clicked(e):
        page.navigate("/add_expense")

    def add_budget_clicked(e):
        page.navigate("/add_budget")

    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                padding=ft.Padding.only(left=28, top=20, bottom=12),
                content=ft.Text(
                    f"Hello, {current_user.get_username()}" , theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                ),
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Dashboard",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.GROUP_ADD_OUTLINED,
                selected_icon=ft.Icons.GROUP_ADD,
                label="Create Groups",
                #on_click=function1,
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.ATTACH_MONEY_OUTLINED,
                selected_icon=ft.Icons.ATTACH_MONEY,
                label="Budget",
                
            ),
        ],
    )

    
    async def handle_show_drawer(e):
        await page.show_drawer()


    return ft.View(
        route="/core",
        drawer= drawer,
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=add_expense_clicked,
        ),
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
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
                        ft.FilledButton(content=ft.Text("Logout"), on_click = logout_clicked),
                    ]
                )
            )
        ],
    )

    
