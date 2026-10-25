import flet as ft
import views.user
from views.user import current_user
from db import supabase

# Main Menu Screen

def build_main_menu_view(page: ft.Page):

    expenses = views.user.current_user.get_expenses()
    default_count = 5
    visible_count = default_count
    expense_list = ft.Column(spacing=0)


    #This updates and builds the tiles, as well as gives them their functionality ======================================
    def render_list():
        expense_list.controls.clear()

        for expense in expenses[:visible_count]:
            expense_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT_LONG),
                    title=ft.Text(expense["label"]),
                    subtitle=ft.Text(expense["created_at"][:10]),
                    trailing=ft.Text(f"${float(expense['amount']):,.2f}", size=20),
                    on_click=lambda e, expense=expense: open_edit_dialog(expense),
                )
            )

        buttons=[]
        if len(expenses) > visible_count:
            buttons.append(
                ft.TextButton(
                    "Show more",
                    icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                    on_click=show_more,
                )
            )
        if visible_count > default_count:
            buttons.append(
                ft.TextButton(
                    "Show less",
                    icon=ft.Icons.KEYBOARD_ARROW_UP,
                    on_click=show_less,
                )
            )
        if buttons:
            expense_list.controls.append(
                ft.Row(buttons, alignment=ft.MainAxisAlignment.CENTER)
            )

    def show_more(e):
        nonlocal visible_count
        visible_count += default_count
        render_list()
        expense_list.update()

    def show_less(e):
        nonlocal visible_count
        visible_count = default_count
        render_list()
        expense_list.update()

    # This is the end of the buttons ===================================================================================

    # Now this is the edit boxes when clicking on a tile ===============================================================
    def open_edit_dialog(expense):
        label_field = ft.TextField(label="Label", value=expense["label"])
        amount_field = ft.TextField(
            label="Amount",
            value=str(expense["amount"]),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        def save(e):
            label = label_field.value.strip()
            try:
                amount = float(amount_field.value.strip())
            except (TypeError, ValueError):
                amount_field.error_text = "enter a number"
                amount_field.update()
                return
            if not label:
                label_field.error_text = "Required"
                label_field.update()
                return

            if views.user.current_user.update_expense(expense["id"], label, amount):
                expense["label"] = label
                expense["amount"] = amount
                page.pop_dialog()
                render_list()
                expense_list.update()

        page.show_dialog(
            ft.AlertDialog(
                title="Edit expense",
                content=ft.Column([label_field, amount_field], tight=True),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.TextButton("Save", on_click=save),
                ]
            )
        )

    # This is the end of the end of the dialogue boxes =================================================================

    render_list()

    def logout_clicked(e):
        current_user.logout
        page.navigate("/login")

    def add_expense_clicked(e):
        page.navigate("/add_expense")

    def add_budget_clicked(e):
        page.navigate("/add_budget")

    def add_groups_clicked(e):
        page.navigate("/add_groups")

    def transfer_funds_clicked(e):
        page.navigate("/transfer_funds")

    def settings_clicked(e):
        page.navigate("/settings")

    async def handle_show_drawer(e):
        await page.show_drawer()

    async def handle_drawer_change(e):
        await page.close_drawer()
        index = e.control.selected_index
        if index == 0:
            page.navigate("/core")
        elif index == 1:
            page.navigate("/add_groups")
        elif index == 2:
            page.navigate("/transfer_funds")
        elif index == 3:
            page.navigate("/add_budget")
        elif index == 4:
            page.navigate("/summary")
        elif index == 5:
            page.navigate("/settings")

    drawer = ft.NavigationDrawer(
        on_change=handle_drawer_change,
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
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SEND_OUTLINED,
                selected_icon=ft.Icons.SEND,
                label="Transfer Funds",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.ATTACH_MONEY_OUTLINED,
                selected_icon=ft.Icons.ATTACH_MONEY,
                label="Budget",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.DESCRIPTION_OUTLINED,
                selected_icon=ft.Icons.DESCRIPTION,
                label="Summary",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )


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
                        ft.Text("Recent expenses", size=18, weight=ft.FontWeight.BOLD),
                        expense_list,
                        ft.FilledButton(content=ft.Text("Logout"), on_click = logout_clicked),
                    ]
                )
            )
        ],
    )

    
