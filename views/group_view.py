import flet as ft
import views.user
from views.widgets import PALETTE, money, cents, tag_name

UNKNOWN_COLOR = "#9E9E9E"


def build_group_view(page: ft.Page):
    user = views.user.current_user
    group = user.current_group

    def go_back(e):
        page.navigate("/add_groups")

    if group is None:
        return ft.View(
            route="/group",
            controls=[
                ft.SafeArea(
                    ft.Column(
                        [
                            ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                            ft.Text("No group selected."),
                        ]
                    )
                )
            ],
        )

    group_id = group["id"]
    is_owner = group["owner_id"] == user.user_id
    members = user.get_group_members(group_id)
    payments = user.get_group_payments(group_id)

    # One consistent color per member, in the order they joined
    member_colors = {m["user_id"]: PALETTE[i % len(PALETTE)] for i, m in enumerate(members)}

    members_row = ft.Row(wrap=True, spacing=12, run_spacing=6)
    payment_list = ft.Column(spacing=12)

    # ---------- helpers ----------

    def paid_total(p):
        return round(sum(float(c["amount"]) for c in p["group_contributions"]), 2)

    def is_full(p):
        return paid_total(p) >= float(p["amount"])

    # Using cards to show posted amounts and completed expenses ========================================================

    def payment_card(p):
        goal = float(p["amount"])
        paid = paid_total(p)
        remaining = round(goal - paid, 2)
        full = remaining <= 0

        # Total per contributor
        per_user = {}
        for c in p["group_contributions"]:
            entry = per_user.setdefault(c["user_id"], {"amount": 0, "profile": c.get("profiles")})
            entry["amount"] += float(c["amount"])

        segments = []
        legend = []
        for uid, info in sorted(per_user.items(), key=lambda item: -item[1]["amount"]):
            color = member_colors.get(uid, UNKNOWN_COLOR)
            name = tag_name(info["profile"])
            segments.append(
                ft.Container(
                    expand=cents(info["amount"]),
                    height=16,
                    bgcolor=color,
                    tooltip=f"{name}: {money(info['amount'])}",
                )
            )
            legend.append(
                ft.Row(
                    [
                        ft.Container(width=10, height=10, border_radius=5, bgcolor=color),
                        ft.Text(f"{name}  {money(info['amount'])}", size=12),
                    ],
                    spacing=6,
                    tight=True,
                )
            )

        if remaining > 0:
            segments.append(ft.Container(expand=cents(remaining), height=16))

        creator = p.get("creator")
        posted = f"Posted by {tag_name(creator)} · {p['created_at'][:10]}"

        if full:
            action = ft.Row(
                [ft.Icon(ft.Icons.CHECK_CIRCLE, size=18), ft.Text("Paid")],
                spacing=6,
            )
        else:
            action = ft.FilledButton(
                content=ft.Text(f"Contribute ({money(remaining)} left)"),
                on_click=lambda e, p=p, remaining=remaining: open_contribute_dialog(p, remaining),
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(p["title"], size=18, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"{money(paid)} / {money(goal)}", weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    ft.Text(posted, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(
                        content=ft.Row(segments, spacing=0),
                        height=16,
                        border_radius=8,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Row(legend, wrap=True, spacing=12, run_spacing=6)
                    if legend
                    else ft.Text("No contributions yet.", size=12, italic=True),
                    action,
                ],
                spacing=8,
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            opacity=0.5 if full else 1.0,
        )

    # Display members and cards ========================================================================================

    def render():
        active = [m for m in members if m["status"] == "member"]
        pending = len(members) - len(active)

        members_row.controls = [
            ft.Row(
                [
                    ft.Container(
                        width=10, height=10, border_radius=5,
                        bgcolor=member_colors.get(m["user_id"], UNKNOWN_COLOR),
                    ),
                    ft.Text(tag_name(m.get("profiles")), size=13),
                ],
                spacing=6,
                tight=True,
            )
            for m in active
        ]
        if pending:
            members_row.controls.append(
                ft.Text(f"+{pending} pending", size=13, italic=True,
                        color=ft.Colors.ON_SURFACE_VARIANT)
            )

        payment_list.controls.clear()
        if not payments:
            payment_list.controls.append(
                ft.Text("No payments yet. Tap + to post one.", italic=True)
            )
        # Unpaid first, paid at the bottom (each keeps newest-first order)
        for p in sorted(payments, key=is_full):
            payment_list.controls.append(payment_card(p))

    def refresh():
        payments[:] = user.get_group_payments(group_id)
        render()
        page.update()

    # dialog box for creating a new post ===============================================================================

    def open_post_dialog(e):
        title_field = ft.TextField(label="What's it for?", max_length=80)
        amount_field = ft.TextField(label="Total amount", keyboard_type=ft.KeyboardType.NUMBER)

        def post(e):
            title_field.error_text = None
            amount_field.error_text = None

            title = str(title_field.value or "").strip()
            if not title:
                title_field.error_text = "Required"
                page.update()
                return
            try:
                amount = round(float(str(amount_field.value or "").strip()), 2)
            except ValueError:
                amount_field.error_text = "Enter a number"
                page.update()
                return
            if amount <= 0:
                amount_field.error_text = "Must be more than $0"
                page.update()
                return

            if user.post_group_payment(group_id, title, amount):
                page.pop_dialog()
                refresh()
            else:
                amount_field.error_text = "Couldn't post payment"
                page.update()

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("New shared payment"),
                content=ft.Column([title_field, amount_field], tight=True, width=320),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton("Post", on_click=post),
                ],
            )
        )

    # dialog box for contributions below ===============================================================================

    def open_contribute_dialog(p, remaining):
        amount_field = ft.TextField(
            label="Your contribution",
            keyboard_type=ft.KeyboardType.NUMBER,
            helper=f"{money(remaining)} remaining",
            expand=True,
        )

        def fill_max(e):
            amount_field.value = f"{remaining:.2f}"
            amount_field.update()

        def submit(e):
            amount_field.error_text = None
            try:
                amount = round(float(str(amount_field.value or "").strip()), 2)
            except ValueError:
                amount_field.error_text = "Enter a number"
                amount_field.update()
                return
            if amount <= 0:
                amount_field.error_text = "Must be more than $0"
                amount_field.update()
                return
            if amount > remaining:
                amount_field.error_text = f"Max is {money(remaining)}"
                amount_field.update()
                return

            ok, message = user.contribute(p["id"], amount)
            if ok:
                page.pop_dialog()
                refresh()
                page.show_dialog(
                    ft.SnackBar(ft.Text(f"Contributed {money(amount)}. Added to your expenses."))
                )
            else:
                amount_field.error_text = message or "Couldn't contribute"
                amount_field.update()

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(f"Contribute to {p['title']}"),
                content=ft.Column(
                    [
                        ft.Row(
                            [amount_field, ft.TextButton("Max", on_click=fill_max)],
                        ),
                    ],
                    tight=True,
                    width=320,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton("Contribute", on_click=submit),
                ],
            )
        )

    def other_members():
        return [
            m for m in members
            if m["status"] == "member" and m["user_id"] != user.user_id
        ]

    def finish(message):
        user.current_group = None
        page.navigate("/add_groups")
        page.show_dialog(ft.SnackBar(ft.Text(message)))

    def confirm_leave(e):
        others = other_members()
        if not others:
            message = (
                "You're the last member, so this group and all its payments will be "
                "deleted. Your contributions stay on your dashboard as expenses."
            )
        elif is_owner:
            message = (
                f"Ownership will pass to {tag_name(others[0].get('profiles'))}. "
                "You'll need a new invite to rejoin."
            )
        else:
            message = "You'll need a new invite to rejoin."

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(f"Leave {group['name']}?"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton(
                        "Leave",
                        on_click=leave,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
                    ),
                ],
            )
        )

    def leave(e):
        result = user.leave_group(group_id)
        page.pop_dialog()
        if result == "deleted":
            finish(f"You left and {group['name']} was deleted.")
        elif result == "transferred":
            finish(f"You left {group['name']}. Ownership was passed on.")
        elif result == "left":
            finish(f"You left {group['name']}.")
        else:
            page.show_dialog(ft.SnackBar(ft.Text("Couldn't leave the group.")))

    def confirm_delete_group(e):
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(f"Delete {group['name']}?"),
                content=ft.Text(
                    "This deletes the group and all its payments for everyone. "
                    "Everyone's contributions stay on their dashboards as expenses."
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton(
                        "Delete group",
                        on_click=delete_group,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
                    ),
                ],
            )
        )

    def delete_group(e):
        page.pop_dialog()
        if user.delete_group(group_id):
            finish(f"{group['name']} was deleted.")
        else:
            page.show_dialog(ft.SnackBar(ft.Text("Couldn't delete the group.")))

    render()

    return ft.View(
        route="/group",
        scroll=ft.ScrollMode.AUTO,
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Post a shared payment",
            on_click=open_post_dialog,
        ),
        controls=[
            ft.SafeArea(
                ft.Column(
                    [
                        ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                        ft.Text(group["name"], size=25, weight=ft.FontWeight.BOLD),
                        ft.Text("Members", size=14, weight=ft.FontWeight.BOLD),
                        members_row,
                        ft.Text("Payments", size=18, weight=ft.FontWeight.BOLD),
                        payment_list,
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    content=ft.Text("Leave group"),
                                    icon=ft.Icons.LOGOUT,
                                    on_click=confirm_leave,
                                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                                ),
                            ]
                            + (
                                [
                                    ft.OutlinedButton(
                                        content=ft.Text("Delete group"),
                                        icon=ft.Icons.DELETE_FOREVER,
                                        on_click=confirm_delete_group,
                                        style=ft.ButtonStyle(color=ft.Colors.ERROR),
                                    )
                                ]
                                if is_owner
                                else []
                            ),
                            wrap=True,
                        ),
                    ],
                    spacing=12,
                )
            )
        ],
    )