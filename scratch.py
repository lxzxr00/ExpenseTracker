import flet as ft

def main(page: ft.Page):

    page.title = "Expense Tracker"
    page.adaptive = True
    page.window.width = 412
    page.window.height = 915

    username_field = ft.TextField(keyboard_type=ft.KeyboardType.TEXT)
    password_field = ft.TextField(keyboard_type=ft.KeyboardType.TEXT, password=True)

    def log_in_clicked(e):
        print("Username entered : ", username_field.value)
        print("Password entered : ", password_field.value)

    def create_account(e):
        page.navigate("/signup")  # sync navigation replaces page.go()

    def route_change(e):
        page.views.clear()

        # Login view — route "/"
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Text(
                                        "Expense Tracker V1",
                                        size=25,
                                        weight=ft.FontWeight.BOLD,
                                        font_family="Roboto",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    width=float("inf"),
                                    padding=ft.Padding(0, 50, 0, 50),
                                ),
                                ft.Text("Username : "),
                                ft.Container(username_field, alignment=ft.Alignment(0, 0)),
                                ft.Text("Password: "),
                                ft.Container(password_field, alignment=ft.Alignment(0, 0)),
                                ft.FilledButton(content=ft.Text("Log in"), on_click=log_in_clicked),
                                ft.FilledButton(content=ft.Text("Create"), on_click=create_account),
                            ]
                        )
                    )
                ],
            )
        )

        # Signup view — route "/signup"
        if page.route == "/signup":
            page.views.append(
                ft.View(
                    route="/signup",
                    controls=[
                        ft.SafeArea(
                            ft.Column(
                                [
                                    ft.Text("Create Account", size=25, weight=ft.FontWeight.BOLD),
                                    ft.FilledButton("Back to login", on_click=lambda e: page.navigate("/")),
                                ]
                            )
                        )
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change
    route_change(None)  # build the initial view directly

ft.run(main)