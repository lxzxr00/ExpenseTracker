import flet as ft
import views.user
from datetime import date, datetime, time
from views.widgets import money

UNCATEGORIZED_COLOR = "#9E9E9E"

def build_summary_view(page: ft.Page):
    user = views.user.current_user
    categories = user.get_categories()

    start_date = date.today().replace(day=1)  # default: start of this month
    date_label = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    overview = ft.Column(spacing=4)
    results = ft.Column(spacing=12)

    # Flet has a built-in Calendar picker, so we're using that =========================================================

    def on_date_picked(e):
        nonlocal start_date
        picked = e.control.value
        if picked:
            start_date = picked.date() if isinstance(picked, datetime) else picked
            load()
            page.update()

    picker = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime.now(),
        on_change=on_date_picked,
    )

    def open_picker(e):
        picker.value = datetime.combine(start_date, time.min)
        page.show_dialog(picker)

    # Building the card with the progress bar ==========================================================================

    def category_card(name, color, spent, budget, items):
        header = ft.Row(
            [
                ft.Container(width=12, height=12, border_radius=6, bgcolor=color),
                ft.Text(name, weight=ft.FontWeight.BOLD, expand=True),
                ft.Text(
                    f"{money(spent)} / {money(budget)}" if budget is not None else money(spent),
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=8,
        )

        body: list[ft.Control] = [header]

        if budget is not None and budget > 0:
            over = spent >= budget
            body.append(
                ft.ProgressBar(
                    value=max(0, min(spent / budget, 1)),
                    color=ft.Colors.RED if over else ft.Colors.GREEN,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    bar_height=10,
                    border_radius=5,
                )
            )
            if spent > budget:
                status = ft.Text(f"{money(spent - budget)} over budget", color=ft.Colors.RED)
            elif spent == budget:
                status = ft.Text("Right at budget", color=ft.Colors.RED)
            else:
                status = ft.Text(f"{money(budget - spent)} under budget", color=ft.Colors.GREEN)
            body.append(status)
        else:
            body.append(
                ft.Text("No budget set", size=12, italic=True,
                        color=ft.Colors.ON_SURFACE_VARIANT)
            )

        if items:
            body.append(
                ft.ExpansionTile(
                    title=ft.Text(
                        f"{len(items)} transaction{'s' if len(items) != 1 else ''}",
                        size=14,
                    ),
                    controls=[
                        ft.ListTile(
                            dense=True,
                            title=ft.Text(x["label"]),
                            subtitle=ft.Text(x["created_at"][:10]),
                            trailing=ft.Text(money(x["amount"])),
                        )
                        for x in items
                    ],
                )
            )
        else:
            body.append(
                ft.Text("No transactions in this period", size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT)
            )

        return ft.Container(
            content=ft.Column(body, spacing=8),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )

    # Filling the categories ===========================================================================================

    def load():
        start_iso = datetime.combine(start_date, time.min).astimezone().isoformat()
        expenses = user.get_expenses_since(start_iso)

        date_label.value = f"{start_date:%b %d, %Y} – today"

        # Group expenses by category
        by_category = {}
        for x in expenses:
            by_category.setdefault(x.get("category_id"), []).append(x)

        def total(items):
            return round(sum(float(x["amount"]) for x in items), 2)

        cards = []

        # Every category that has a budget or spending in this period ==================================================
        rows = []
        for c in categories:
            items = by_category.get(c["id"], [])
            budget = float(c["budget"]) if c["budget"] is not None else None
            if items or budget is not None:
                rows.append((c["name"], c["color"], total(items), budget, items))
        rows.sort(key=lambda r: -r[2])  # biggest spending first

        for name, color, spent, budget, items in rows:
            cards.append(category_card(name, color, spent, budget, items))

        # Uncategorized last
        uncategorized = by_category.get(None, [])
        if uncategorized:
            cards.append(
                category_card("Uncategorized", UNCATEGORIZED_COLOR,
                              total(uncategorized), None, uncategorized)
            )

        # Overview numbers =============================================================================================
        spent_total = total(expenses)
        budget_total = round(
            sum(float(c["budget"]) for c in categories if c["budget"] is not None), 2
        )
        over_count = sum(1 for _, _, spent, budget, _ in rows
                         if budget is not None and budget > 0 and spent >= budget)

        overview.controls = [
            ft.Text(f"{money(spent_total)} spent", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(
                f"Budget total: {money(budget_total)}" if budget_total > 0
                else "No budgets set",
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            ft.Text(
                f"{len(expenses)} transaction{'s' if len(expenses) != 1 else ''}",
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
        ]
        if over_count:
            overview.controls.append(
                ft.Text(
                    f"{over_count} categor{'y is' if over_count == 1 else 'ies are'} "
                    "at or over budget",
                    color=ft.Colors.RED,
                )
            )

        results.controls = cards or [
            ft.Text("No transactions in this period.", italic=True)
        ]


    def go_back(e):
        page.navigate("/core")

    load()

    return ft.View(
        route="/summary",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.SafeArea(
                ft.Column(
                    [
                        ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                        ft.Text("Summary", size=25, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("Showing", size=12,
                                                color=ft.Colors.ON_SURFACE_VARIANT),
                                        date_label,
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.OutlinedButton(
                                    content=ft.Text("Change date"),
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    on_click=open_picker,
                                ),
                            ]
                        ),
                        ft.Container(
                            content=overview,
                            padding=20,
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                            width=float("inf"),
                        ),
                        ft.Text("By category", size=18, weight=ft.FontWeight.BOLD),
                        results,
                    ],
                    spacing=12,
                )
            )
        ],
    )