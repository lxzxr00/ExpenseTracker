import flet as ft
import views.user
from views.widgets import money, tag_name

RECENT_COUNT = 3
CARD_HEIGHT = 110


def build_transfer_funds_view(page: ft.Page):
    user = views.user.current_user
    me = user.user_id
    transfers = user.get_transfers()

    search_field = ft.TextField(
        label="Search display names",
        hint_text="e.g. Rice or Rice#4821",
        on_submit=lambda e: run_search(),
        expand=True,
    )
    results_section = ft.Column(spacing=8, visible=False)
    recent_section = ft.Column(spacing=8)
    activity_section = ft.Column(spacing=8)


    def avatar(profile):
        return ft.CircleAvatar(
            content=ft.Text(profile["display_name"][0].upper()),
            radius=20,
        )

    def profile_card(profile):
        return ft.Container(
            height=CARD_HEIGHT,
            padding=12,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            avatar(profile),
                            ft.Text(tag_name(profile), weight=ft.FontWeight.BOLD, expand=True),
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                content=ft.Text("Request"),
                                icon=ft.Icons.CALL_RECEIVED,
                                on_click=lambda e, p=profile: open_amount_dialog(p, "request"),
                            ),
                            ft.FilledButton(
                                content=ft.Text("Send"),
                                icon=ft.Icons.SEND,
                                on_click=lambda e, p=profile: open_amount_dialog(p, "send"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=8,
            ),
        )

    # Empty Cards ======================================================================================================

    def placeholder_card():
        return ft.Container(
            height=CARD_HEIGHT,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            opacity=0.5,
        )

    def recent_profiles():
        seen = set()
        recent = []
        for t in transfers:
            if t["initiated_by"] != me:
                continue
            other = t["payee"] if t["from_user"] == me else t["payer"]
            if not other or other["id"] in seen:
                continue
            seen.add(other["id"])
            recent.append(other)
            if len(recent) == RECENT_COUNT:
                break
        return recent

    # Function to build an activity card ===============================================================================

    def activity_card(icon, title, note, detail, buttons, icon_color=None):
        lines = [ft.Text(title, weight=ft.FontWeight.BOLD)]
        if note:
            lines.append(ft.Text(f"“{note}”", italic=True))
        if detail:
            lines.append(ft.Text(detail, size=12, color=ft.Colors.ON_SURFACE_VARIANT))
        return ft.Container(
            padding=12,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, color=icon_color),
                            ft.Column(lines, spacing=2, expand=True),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Row(buttons, alignment=ft.MainAxisAlignment.END),
                ],
                spacing=8,
            ),
        )


    # Building your bottm cards ========================================================================================
    def build_activity():
        cards = []
        for t in transfers:
            amount = money(t["amount"])
            payer = tag_name(t.get("payer"))
            payee = tag_name(t.get("payee"))
            note = t.get("note")
            tid = t["id"]

            # Requests waiting on you
            if t["kind"] == "request" and t["status"] == "pending" and t["from_user"] == me:
                cards.append(activity_card(
                    ft.Icons.REQUEST_PAGE,
                    f"{payee} requests {amount}",
                    note,
                    None,
                    [
                        ft.TextButton(
                            "Decline",
                            on_click=lambda e, tid=tid: act(user.decline_request, tid, "Request declined."),
                            style=ft.ButtonStyle(color=ft.Colors.ERROR),
                        ),
                        ft.FilledButton(
                            "Pay",
                            on_click=lambda e, t=t: confirm_pay(t),
                        ),
                    ],
                    icon_color=ft.Colors.PRIMARY,
                ))

            # Requests you made that are still waiting
            elif t["kind"] == "request" and t["status"] == "pending" and t["to_user"] == me:
                cards.append(activity_card(
                    ft.Icons.HOURGLASS_EMPTY,
                    f"Waiting on {payer} for {amount}",
                    note,
                    None,
                    [
                        ft.TextButton(
                            "Cancel request",
                            on_click=lambda e, tid=tid: act(user.cancel_request, tid, "Request cancelled."),
                        ),
                    ],
                ))

            # Finished items addressed to you
            elif t["to_user"] == me and not t["dismissed"]:
                dismiss = [
                    ft.TextButton(
                        "Dismiss",
                        on_click=lambda e, tid=tid: act(user.dismiss_transfer, tid, None),
                    )
                ]
                if t["status"] == "completed" and t["kind"] == "send":
                    cards.append(activity_card(
                        ft.Icons.CALL_RECEIVED,
                        f"{payer} sent you {amount}",
                        note,
                        f"Added to your dashboard as {money(-float(t['amount']))}",
                        dismiss,
                        icon_color=ft.Colors.PRIMARY,
                    ))
                elif t["status"] == "completed" and t["kind"] == "request":
                    cards.append(activity_card(
                        ft.Icons.CHECK_CIRCLE,
                        f"{payer} paid your {amount} request",
                        note,
                        f"Added to your dashboard as {money(-float(t['amount']))}",
                        dismiss,
                        icon_color=ft.Colors.PRIMARY,
                    ))
                elif t["status"] == "declined":
                    cards.append(activity_card(
                        ft.Icons.CANCEL,
                        f"{payer} declined your {amount} request",
                        note,
                        None,
                        dismiss,
                        icon_color=ft.Colors.ERROR,
                    ))
        return cards

    # Showing you your most interacted with profiles ===================================================================

    def render():
        recent = recent_profiles()
        recent_section.controls = [profile_card(p) for p in recent] + [
            placeholder_card() for _ in range(RECENT_COUNT - len(recent))
        ]

        cards = build_activity()
        activity_section.controls = cards or [
            ft.Text("Nothing here yet.", italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
        ]

    def refresh():
        transfers[:] = user.get_transfers()
        render()
        page.update()


    # USed to confirm that the message was successful on your end ======================================================
    def act(action, transfer_id, success_message):
        ok, message = action(transfer_id)
        if ok:
            refresh()
            if success_message:
                page.show_dialog(ft.SnackBar(ft.Text(success_message)))
        else:
            page.show_dialog(ft.SnackBar(ft.Text(message or "Something went wrong.")))
            refresh()

    # Run a search for profiles ========================================================================================

    def run_search():
        found = user.search_profiles(str(search_field.value or ""))
        results_section.controls = [
            ft.Row(
                [
                    ft.Text("Results", size=16, weight=ft.FontWeight.BOLD, expand=True),
                    ft.TextButton("Clear", on_click=clear_search),
                ]
            )
        ]
        if found:
            results_section.controls += [profile_card(p) for p in found]
        else:
            results_section.controls.append(ft.Text("No matches.", italic=True))
        results_section.visible = True
        page.update()


    # Empty the search bar =============================================================================================

    def clear_search(e=None):
        search_field.value = ""
        results_section.controls.clear()
        results_section.visible = False
        page.update()

    # Send and Request Dialog boxes ====================================================================================

    def open_amount_dialog(profile, kind):
        sending = kind == "send"
        amount_field = ft.TextField(label="Amount", keyboard_type=ft.KeyboardType.NUMBER)
        note_field = ft.TextField(label="Note (optional)", max_length=60)

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

            note = str(note_field.value or "").strip()
            if sending:
                ok, message = user.send_money(profile["id"], amount, note)
                done = f"Sent {money(amount)} to {tag_name(profile)}. Added to your expenses."
            else:
                ok, message = user.request_money(profile["id"], amount, note)
                done = f"Requested {money(amount)} from {tag_name(profile)}."

            if ok:
                page.pop_dialog()
                clear_search()
                refresh()
                page.show_dialog(ft.SnackBar(ft.Text(done)))
            else:
                amount_field.error_text = message or "Something went wrong"
                amount_field.update()

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(
                    f"{'Send to' if sending else 'Request from'} {tag_name(profile)}"
                ),
                content=ft.Column(
                    [
                        amount_field,
                        note_field,
                        ft.Text(
                            "The note becomes the expense label on both dashboards.",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    tight=True,
                    width=320,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton("Send" if sending else "Request", on_click=submit),
                ],
            )
        )

    # Dialog box to confirm payment ====================================================================================

    def confirm_pay(t):
        def pay(e):
            page.pop_dialog()
            act(user.pay_request, t["id"], f"Paid {money(t['amount'])}. Added to your expenses.")

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(f"Pay {tag_name(t.get('payee'))} {money(t['amount'])}?"),
                content=ft.Text(f"{money(t['amount'])} will be added to your expenses."),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                    ft.FilledButton("Pay", on_click=pay),
                ],
            )
        )


    def go_back(e):
        page.navigate("/core")

    render()

    return ft.View(
        route="/transfer_funds",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.SafeArea(
                ft.Column(
                    [
                        ft.FilledButton(content=ft.Text("Go back"), on_click=go_back),
                        ft.Text("Transfer Funds", size=25, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                search_field,
                                ft.IconButton(icon=ft.Icons.SEARCH, on_click=lambda e: run_search()),
                            ]
                        ),
                        results_section,
                        ft.Text("Recent", size=18, weight=ft.FontWeight.BOLD),
                        recent_section,
                        ft.Text("Activity", size=18, weight=ft.FontWeight.BOLD),
                        activity_section,
                    ],
                    spacing=12,
                )
            )
        ],
    )