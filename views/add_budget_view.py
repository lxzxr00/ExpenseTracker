import flet as ft
import views.user
from views.user import user_account, current_user
from views.widgets import money


# The colors that we'll use for the categories  ========================================================================
PALETTE = [
    "#E57373", "#F06292", "#BA68C8", "#7986CB", "#4FC3F7",
    "#4DB6AC", "#81C784", "#FFD54F", "#FFB74D", "#A1887F",
]


def build_add_budget_view(page: ft.Page):
    user = views.user.current_user
    categories = user.get_categories()

    total_text = ft.Text(size=32, weight=ft.FontWeight.BOLD)
    summary_text = ft.Text(color=ft.Colors.ON_SURFACE_VARIANT)
    category_list = ft.Column(spacing=0)


    def render():
        total = sum(float(c["budget"]) for c in categories if c["budget"] is not None)
        total_text.value = money(total)
        count = len(categories)
        summary_text.value = f"Across {count} {'category' if count == 1 else 'categories'}"

        category_list.controls.clear()
        if not categories:
            category_list.controls.append(
                ft.Text("No categories yet. Add one below", italic=True)
            )
        for c in categories:
            category_list.controls.append(
                ft.ListTile(
                    leading = ft.Container(
                        width=20, height=20, border_radius=10, bgcolor=c["color"]
                    ),
                    title = ft.Text(c["name"]),
                    trailing = ft.Text(
                        money(c["budget"]) if c["budget"] is not None else "Limit not set",
                        size=20,
                    ),
                    on_click=lambda e, c=c: open_category_dialog(c),

                )
            )

    def refresh():
        categories[:] = user.get_categories()
        render()
        page.update()

    def open_category_dialog(category=None):
        editing = category is not None

        name_field = ft.TextField(
            label="Category Name",
            value=category["name"] if editing else "",
        )
        budget_field = ft.TextField(
            label="Budget",
            value=category["budget"] if editing and category["budget"] is not None else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        selected = {"color": category["color"] if editing else PALETTE[0]}
        color_row = ft.Row(wrap=True, spacing=8, run_spacing=8)

        def render_colors():
            color_row.controls = [
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=16,
                    bgcolor=col,
                    border=ft.Border.all(3, ft.Colors.ON_SURFACE)
                    if col == selected["color"]
                    else None,
                    on_click=lambda e, col=col: pick_color(col),
                )
                for col in PALETTE
            ]

        def pick_color(col):
            selected["color"] = col
            render_colors()
            color_row.update()

        def save(e):
            name = str(name_field.value or "").strip()
            if not name:
                name_field.error_text = "Required"
                name_field.update()
                return

            raw = str(budget_field.value or "").strip()
            budget = None
            if raw:
                try:
                    budget = float(raw)
                except ValueError:
                    budget_field.error_text = "Enter a number"
                    budget_field.update()
                    return
                if budget < 0:
                    budget_field.error_text = "Can't be negative"
                    budget_field.update()
                    return

            if editing:
                ok = user.update_category(category["id"], name, selected["color"], budget)
            else:
                ok = user.add_category(name, selected["color"], budget)

            if ok:
                page.pop_dialog()
                refresh()
            else:
                name_field.error_text = "Couldn't save. Is that name already in use?"
                name_field.update()

        def delete(e):
            if user.delete_category(category["id"]):
                page.pop_dialog()
                refresh()

        actions = []
        if editing:
            actions.append(
                ft.TextButton(
                    "Delete",
                    on_click=delete,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR)
                )
            )
        actions += [
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.TextButton("Save", on_click=save),
        ]

        render_colors()
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Edit category" if editing else "New category"),
                content=ft.Column(
                    [name_field, ft.Text("Color"), color_row, budget_field],
                    tight=True,
                    width=320,
                ),
                actions=actions,
            )
        )

    def go_back(e):
        page.navigate("/core")

    render()

    return ft.View(
        route="/add_budget",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.SafeArea(
                ft.Column(
                    [
                        ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Total budget"),
                                    total_text,
                                    summary_text,
                                ],
                                spacing=4,
                            ),
                            padding=20,
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            width=float("inf"),
                        ),
                        ft.Text("Categories", size=18, weight=ft.FontWeight.BOLD),
                        category_list,
                        ft.FilledButton(
                            content=ft.Text("Add category"),
                            icon=ft.Icons.ADD,
                            on_click=lambda e: open_category_dialog(),
                        ),
                    ],
                    spacing=16,
                )
            )
        ],
    )