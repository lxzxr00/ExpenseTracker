import flet as ft

NO_CATEGORY = "none"


def money(value):
    return f"${float(value):,.2f}"

def category_dropdown(categories, selected_id=None):
    return ft.Dropdown(
        label="Category",
        value=str(selected_id) if selected_id is not None else NO_CATEGORY,
        options=[ft.dropdown.Option(key=NO_CATEGORY, text="No category")]
        + [ft.dropdown.Option(key=str(c["id"]), text=c["name"]) for c in categories],
    )


def selected_category_id(dropdown):
    value = dropdown.value
    if value in (None, "", NO_CATEGORY):
        return None
    return int(value)