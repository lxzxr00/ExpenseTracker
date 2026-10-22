import flet as ft
from views.login_view import build_login_view
from views.signup_view import build_signup_view
from views.core_view import build_main_menu_view
from views.add_expense_view import build_add_expense_view

# Navigation in flet is hierarchal, PAGES have multiple VIEWS inside of them
# A PAGE is the main window or browser session that is created for the application
# A VIEW is an individual screen or ROUTE stacked inside the PAGE


def main(page : ft.Page,):

    # Page dimensions to mimic phone dimensions
    page.title = "Expense Tracker"
    page.adaptive = True
    page.window.width = 412
    page.window.height = 915

    #The main function that will direct user traffic between VIEWS
    def route_change(e):
        page.views.clear()

        # This is the default page right now, the login page
        page.views.append(build_login_view(page))

        # This is how the program knows which page to show you, by updating the ROUTE
        # WHEN YOU MAKE A VIEW, PUT IT IN HERE
        if page.route == "/signup":
            page.views.append(build_signup_view(page))
        if page.route == "/core":
            page.views.append(build_main_menu_view(page))
        if page.route == "/login":
            page.views.append(build_login_view(page))
        if page.route == "/add_expense":
            page.views.append(build_add_expense_view(page))
        if page.route == "/add_budget":
            page.views.append(build_add_budget_view(page))

        # Always need to update the page after the route is changed, so that you see the new page
        page.update()

    # You shouldn't have to touch anything past this point =============================================================
    # This just says current route is now the route that was grabbed from whatever changes happened in the program
    page.on_route_change = route_change
    # Says the Initial route is nothing "/"
    route_change(None)

ft.run(main)