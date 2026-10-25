import flet as ft
import views.user
from views.user import current_user
from views.widgets import category_dropdown, selected_category_id, money


# Main Menu Screen

def build_main_menu_view(page: ft.Page):

    expenses = views.user.current_user.get_expenses()
    categories = views.user.current_user.get_categories()
    categories_by_id = {c["id"]: c for c in categories}
    default_count = 5
    visible_count = default_count
    expense_list = ft.Column(spacing=0)
    UNCATEGORIZED_COLOR = "#9E9E9E"
    summary = ft.Column(spacing=12)

    def cents(value):
        return int(round(value * 100))

    # This is the Dashboard that displays the expenses per category ====================================================
    # Flet doesn't have a widget that can use more than one color, so we're going to try and make one ==================
    def render_summary():
        # We need to add up spending by category first
        totals = {}
        for expense in expenses:
            cid = expense.get("category_id")
            totals[cid] = totals.get(cid, 0) + float(expense["amount"])

        spent = round(sum(totals.values()), 2)
        budget = round(sum(float(c["budget"]) for c in categories if c["budget"] is not None), 2)

        # Creation of the bar segments with the biggest category first =======================================
        segments = []
        legend = []
        for cid, amount in sorted(totals.items(), key=lambda item: -item[1]):
            if amount <= 0:
                continue
            cat = categories_by_id.get(cid)
            name = cat["name"] if cat else "Uncategorized"
            color = cat["color"] if cat else UNCATEGORIZED_COLOR

            segments.append(
                ft.Container(
                    expand=cents(amount),
                    height=24,
                    bgcolor=color,
                    tooltip=f"{name}: {money(amount)}",
                )
            )
            legend.append(
                ft.Row(
                    [
                        ft.Container(width=12, height=12, border_radius=6, bgcolor=color),
                        ft.Text(f"{name}  {money(amount)}", size=13),
                    ],
                    spacing=6,
                    tight=True,
                )
            )
        # Empty space for the budget that's left =============================================================
        if budget > spent:
            segments.append(ft.Container(expand=cents(budget - spent), height=24))

        # Header Text ========================================================================================
        over = budget > 0 and spent > budget
        if budget > 0:
            headline = f"{money(spent)} of {money(budget)} spent"
            if over:
                detail = ft.Text(f"Over budget by {money(spent - budget)}", color=ft.Colors.ERROR)
            else:
                detail = ft.Text(f"{money(budget - spent)} left", color=ft.Colors.ON_SURFACE_VARIANT)
        else:
            headline = f"{money(spent)} spent"
            detail = ft.Text(
                "Set category budgets on the Budget page to track a limit.",
                color=ft.Colors.ON_SURFACE_VARIANT,
                italic=True,
            )

        # Per category warnings ==============================================================================
        warnings = []
        for c in categories:
            if c["budget"] is None:
                continue
            cat_spent = totals.get(c["id"], 0)
            if cat_spent > float(c["budget"]):
                warnings.append(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ERROR, size=18),
                            ft.Text(
                                f"{c['name']} is over budget by {money(cat_spent - float(c['budget']))}",
                                color=ft.Colors.ERROR,
                            ),
                        ],
                        spacing=6,
                    )
                )

        # Construction =======================================================================================
        summary.controls = [
            ft.Text(
                headline,
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ERROR if over else None,
            ),
            detail,
            ft.Container(
                content=ft.Row(segments, spacing=0),
                height=24,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            ft.Row(legend, wrap=True, spacing=16, run_spacing=8)
            if legend
            else ft.Text("No expenses yet.", italic=True),
            *warnings
        ]

    #This updates and builds the tiles, as well as gives them their functionality ======================================
    def render_list():
        expense_list.controls.clear()

        for expense in expenses[:visible_count]:
            cat = expense.get("categories")
            date = expense["created_at"][:10]
            expense_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.RECEIPT_LONG,
                        color=cat["color"] if cat else ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    title=ft.Text(expense["label"]),
                    subtitle=ft.Text(f"{date} - {cat['name']}" if cat else date),
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

        render_summary()

    def show_more(e):
        nonlocal visible_count
        visible_count += default_count
        render_list()
        page.update()

    def show_less(e):
        nonlocal visible_count
        visible_count = default_count
        render_list()
        page.update()

    # This is the end of the buttons ===================================================================================

    # Now this is the edit boxes when clicking on a tile ===============================================================
    def open_edit_dialog(expense):
        label_field = ft.TextField(label="Label", value=expense["label"])
        amount_field = ft.TextField(
            label="Amount",
            value=str(expense["amount"]),
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        category_field = category_dropdown(categories, expense.get("category_id"))

        def save(e):
            label_field.error_text = None
            amount_field.error_text = None

            label = str(label_field.value or "").strip()
            if not label:
                label_field.error_text = "Required"
                label_field.update()
                return
            try:
                amount = float(str(amount_field.value or "").strip())
            except (TypeError, ValueError):
                amount_field.error_text = "enter a number"
                amount_field.update()
                return

            category_id = selected_category_id(category_field)

            if views.user.current_user.update_expense(expense["id"], label, amount, category_id):
                cat = categories_by_id.get(category_id)
                expense["label"] = label
                expense["amount"] = amount
                expense["category_id"] = category_id
                expense["categories"] = (
                    {"name": cat["name"], "color": cat["color"]} if cat else None
                )
                page.pop_dialog()
                render_list()
                page.update()

        def confirm_delete(e):
            page.pop_dialog()
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Delete expense?"),
                    content= ft.Text(
                        f"\"{expense['label']}\" (${float(expense['amount']):,.2f}) "
                        "Will be permanently deleted",
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                        ft.FilledButton(
                            "Delete",
                            on_click=delete,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
                        )
                    ]
                )
            )

        def delete(e):
            if views.user.current_user.delete_expense(expense["id"]):
                expenses.remove(expense)
                page.pop_dialog()
                render_list()
                page.update()


        page.show_dialog(
            ft.AlertDialog(
                title="Edit expense",
                content=ft.Column(
                    [label_field, amount_field, category_field],
                    tight=True,
                    width=320,
                ),
                actions=[
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color=ft.Colors.ERROR),
                    ),
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.TextButton("Save", on_click=save),
                ]
            )
        )

    # This is the end of the end of the dialogue boxes =================================================================

    render_list()

    def logout_clicked(e):
        current_user.logout()
        page.navigate("/login")

    def add_expense_clicked(e):
        page.navigate("/add_expense")

    def add_budget_clicked(e):
        page.navigate("/add_budget")

    def add_groups_clicked(e):
        page.navigate("/add_groups")

    def transfer_funds_clicked(e):
        page.navigate("/transfer_funds")

    def group_expenses_clicked(e):
        page.navigate("/group_expenses")

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
            page.navigate("/group_expenses")
        elif index == 3:
            page.navigate("/transfer_funds")
        elif index == 4:
            page.navigate("/add_budget")
        elif index == 5:
            page.navigate("/summary")
        elif index == 6:
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
                icon=ft.Icons.GROUPS_OUTLINED,
                selected_icon=ft.Icons.GROUPS,
                label="Group Expenses",
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
        scroll=ft.ScrollMode.AUTO,
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
                        ft.Container(
                            content=summary,
                            padding=20,
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                            width=float("inf"),
                        ),
                        ft.Text("Recent expenses", size=18, weight=ft.FontWeight.BOLD),
                        expense_list,
                        ft.FilledButton(content=ft.Text("Logout"), on_click = logout_clicked),
                    ]
                )
            )
        ],
    )

    
