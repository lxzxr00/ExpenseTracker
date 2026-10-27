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
    sort_mode = "newest"
    category_filter = "all"

    # Needed sort function for the user case ===========================================================================
    SORT_OPTIONS = {
        "newest": "Newest first",
        "oldest": "Oldest first",
        "high": "Highest amount",
        "low": "Lowest amount",
    }

    def visible_expenses():
        # Filter by category
        if category_filter == "all":
            items = list(expenses)
        elif category_filter == "none":
            items = [x for x in expenses if x.get("category_id") is None]
        else:
            items = [x for x in expenses if x.get("category_id") == int(category_filter)]

        # Sort
        if sort_mode == "newest":
            items.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_mode == "oldest":
            items.sort(key=lambda x: x["created_at"])
        elif sort_mode == "high":
            items.sort(key=lambda x: float(x["amount"]), reverse=True)
        elif sort_mode == "low":
            items.sort(key=lambda x: float(x["amount"]))
        return items

    def on_sort_change(e):
        nonlocal sort_mode, visible_count
        sort_mode = e.control.value
        visible_count = default_count
        render_list()
        page.update()

    def on_filter_change(e):
        nonlocal category_filter, visible_count
        category_filter = e.control.value
        visible_count = default_count
        render_list()
        page.update()

    def compact_dropdown(**kwargs):
        return ft.Dropdown(
            filled=True,
            fill_color=ft.Colors.SURFACE_CONTAINER_LOW,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=12,
            text_size=14,
            expand=True,
            **kwargs,
        )

    filter_dropdown = compact_dropdown(
        value=category_filter,
        leading_icon=ft.Icons.FILTER_LIST,
        options=[
                    ft.dropdown.Option(key="all", text="All categories"),
                    ft.dropdown.Option(key="none", text="Uncategorized"),
                ]
                + [ft.dropdown.Option(key=str(c["id"]), text=c["name"]) for c in categories],
        on_select=on_filter_change,
    )

    sort_dropdown = compact_dropdown(
        value=sort_mode,
        leading_icon=ft.Icons.SORT,
        options=[ft.dropdown.Option(key=k, text=v) for k, v in SORT_OPTIONS.items()],
        on_select=on_sort_change,
    )
    # ==================================================================================================================

    def cents(value):
        return int(round(value * 100))

    # This is the Dashboard that displays the expenses per category ====================================================
    # Flet doesn't have a widget that can use more than one color, so we're going to try and make one ==================
    def render_summary():
        # We need to add up spending by category first
        # We need to create a dictionary that correlates the category_id with the totals of that category
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
        # Once the amount spent exceeds the budget per category, display a warning near the legend ===========

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
        shown = visible_expenses()

        if not shown:
            expense_list.controls.append(
                ft.Text("No expenses match this filter.", italic=True)
            )

        for expense in shown[:visible_count]:
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
                    trailing=ft.Text(money(expense["amount"]), size=20),
                    on_click=lambda e, expense=expense: open_edit_dialog(expense),
                )
            )

        buttons=[]
        if len(shown) > visible_count:
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
        # Added in for contributions in groups, you cant remove contributions in the dashboard =========================
        is_contribution = expense.get("contribution_id") is not None
        if is_contribution:
            amount_field.disabled = True
            amount_field.helper_text = "Group contribution — amount can't be changed"

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
                # Updates the displayed list and the whole page once the update is complete
                render_list()
                page.update()

        # Because expenses are the most significant value, it asks you if you are sure you want to delete the expense
        # Calls cancel and delete functions
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

        # Meant for the deletion of expense
        def delete(e):
            if views.user.current_user.delete_expense(expense["id"]):
                expenses.remove(expense)
                page.pop_dialog()
                render_list()
                page.update()

        # The dialog mini-view that pops up when you press on a Tile object
        # Calls the confirm delete function and the save function displayed earlier
        actions = []
        if not is_contribution:
            actions.append(
                ft.TextButton(
                    "Delete",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                )
            )
        actions += [
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.FilledButton("Save", on_click=save),
        ]

        # The dialog mini-view that pops up when you press on a Tile object
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Edit expense"),
                content=ft.Column(
                    [label_field, amount_field, category_field],
                    tight=True,
                    width=320,
                ),
                actions=actions,
            )
        )

    # This is the end of the end of the dialogue boxes =================================================================

    render_list()

    def logout_clicked(e):
        current_user.logout()
        page.navigate("/login")

    def add_expense_clicked(e):
        page.navigate("/add_expense")

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


    # Simple Drawer component that correlates to the section above,
    # It houses the buttons that redirect you to other views. DOES NOT INCLUDE THE ADD EXPENSE BUTTON
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
                label="Groups",
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
                        ft.Row(
                            [
                                ft.Text("Expenses", size=18, weight=ft.FontWeight.BOLD, expand=True),
                                sort_dropdown,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        filter_dropdown,
                        expense_list,
                        ft.FilledButton(content=ft.Text("Logout"), on_click = logout_clicked),
                    ]
                )
            )
        ],
    )

    
