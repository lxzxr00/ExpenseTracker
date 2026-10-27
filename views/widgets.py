import flet as ft

NO_CATEGORY = "none"
PALETTE = [
    "#E57373", "#F06292", "#BA68C8", "#7986CB", "#4FC3F7",
    "#4DB6AC", "#81C784", "#FFD54F", "#FFB74D", "#A1887F",
]


def money(value):
    value = float(value)
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"

def cents(value):
    return int(round(float(value) * 100))


def tag_name(profile):
    if not profile:
        return "Unknown"
    return f"{profile['display_name']}#{profile['tag']}"


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