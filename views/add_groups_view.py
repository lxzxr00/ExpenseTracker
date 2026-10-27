import flet as ft
import views.user

def tag_name(profile):
    return f"{profile['display_name']}#{profile['tag']}"


def build_add_groups_view(page: ft.Page):
    user = views.user.current_user
    rows = user.get_groups()

    invites_section = ft.Column(spacing=0)
    group_list = ft.Column(spacing=0)

    # We're going to use Tiles to list the groups you've made and are a part of ========================================
    def render():
        invites = [r for r in rows if r["status"] == "invited"]
        groups = [r for r in rows if r["status"] == "member"]

        invites_section.controls.clear()
        if invites:
            invites_section.controls.append(
                ft.Text("Pending invites", size=18, weight=ft.FontWeight.BOLD)
            )
            for r in invites:
                g = r["groups"]
                invites_section.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.MAIL_OUTLINE),
                        title=ft.Text(g["name"]),
                        subtitle=ft.Text("You've been invited"),
                        trailing=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.CHECK,
                                    tooltip="Accept",
                                    icon_color=ft.Colors.PRIMARY,
                                    on_click=lambda e, gid=g["id"]: accept(gid),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    tooltip="Decline",
                                    icon_color=ft.Colors.ERROR,
                                    on_click=lambda e, gid=g["id"]: decline(gid),
                                ),
                            ],
                            tight=True,
                        ),
                    )
                )

        group_list.controls.clear()
        if not groups:
            group_list.controls.append(
                ft.Text("You're not in any groups yet. Create one below.", italic=True)
            )
        for r in groups:
            g = r["groups"]
            is_owner = g["owner_id"] == user.user_id
            group_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.GROUPS),
                    title=ft.Text(g["name"]),
                    subtitle=ft.Text("Owner" if is_owner else "Member"),
                    on_click=lambda e, g=g: open_group(g),
                )
            )

    def refresh():
        rows[:] = user.get_groups()
        render()
        page.update()

    def accept(group_id):
        if user.accept_invite(group_id):
            refresh()

    def decline(group_id):
        if user.decline_invite(group_id):
            refresh()

    def open_group(group):
        user.current_group = group
        page.navigate("/group")

    # Using a dialog box for group creations =================================================================

    def open_create_dialog(e):
        selected = {}  # user_id -> "Name#1234"

        name_field = ft.TextField(label="Group name", max_length=50)
        search_field = ft.TextField(
            label="Search display names",
            hint_text="e.g. Rice or Rice#4821",
            on_submit=lambda e: run_search(),
            expand=True,
        )
        results = ft.Column(spacing=0)
        chips = ft.Row(wrap=True, spacing=6, run_spacing=6)

        def render_chips():
            chips.controls = [
                ft.Chip(
                    label=ft.Text(label),
                    on_delete=lambda e, uid=uid: remove_invitee(uid),
                )
                for uid, label in selected.items()
            ]

        def run_search():
            found = user.search_profiles(str(search_field.value or ""))
            results.controls.clear()
            if not found:
                results.controls.append(ft.Text("No matches.", italic=True))
            for p in found:
                already = p["id"] in selected
                results.controls.append(
                    ft.ListTile(
                        title=ft.Text(tag_name(p)),
                        trailing=ft.Icon(ft.Icons.CHECK) if already else ft.IconButton(
                            icon=ft.Icons.PERSON_ADD,
                            tooltip="Invite",
                            on_click=lambda e, p=p: add_invitee(p),
                        ),
                    )
                )
            results.update()

        def add_invitee(profile):
            selected[profile["id"]] = tag_name(profile)
            render_chips()
            chips.update()
            run_search()

        def remove_invitee(uid):
            selected.pop(uid, None)
            render_chips()
            chips.update()

        def create(e):
            name = str(name_field.value or "").strip()
            if not name:
                name_field.error_text = "Required"
                name_field.update()
                return
            if user.create_group(name, list(selected.keys())) is not None:
                page.pop_dialog()
                refresh()
            else:
                name_field.error_text = "Couldn't create group"
                name_field.update()

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("New group"),
                content=ft.Column(
                    [
                        name_field,
                        ft.Row(
                            [
                                search_field,
                                ft.IconButton(
                                    icon=ft.Icons.SEARCH,
                                    on_click=lambda e: run_search(),
                                ),
                            ]
                        ),
                        ft.Text("Invited:", weight=ft.FontWeight.BOLD),
                        chips,
                        results,
                    ],
                    tight=True,
                    width=360,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton("Create", on_click=create),
                ],
            )
        )

    def go_back(e):
        page.navigate("/core")

    render()

    return ft.View(
                route = "/add_groups",
                controls = [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                                ft.Text("Groups", size=25, weight=ft.FontWeight.BOLD),
                                invites_section,
                                ft.Text("Your groups", size=18, weight=ft.FontWeight.BOLD),
                                group_list,
                                ft.FilledButton(
                                    content=ft.Text("Create group"),
                                    icon=ft.Icons.ADD,
                                    on_click=open_create_dialog,
                                ),
                            ],
                            spacing=16,
                        )
                    )
                ],
            )