def command():
    import typer
    from IPython import start_ipython  # type: ignore[import]
    from uuid import getnode

    # from conf import settings
    from db import DB
    from crud.common import show_tables
    from crud.user import add_user, get_user, delete_user

    user_ns = {}
    banner = [
        typer.style(
            f'Application Shell',
            fg=typer.colors.MAGENTA,
        )
    ]

    banner.append("")
    user_ns["DB"] = DB
    # user_ns["settings"] = settings
    user_ns["getnode"] = getnode
    user_ns["show_tables"] = show_tables
    user_ns["add_user"] = add_user
    user_ns["get_user"] = get_user
    user_ns["delete_user"] = delete_user

    banner.append(
        "Auto populated vars: " + ", ".join([typer.style(var, fg=typer.colors.GREEN) for var in user_ns.keys()])
    )

    for message in banner:
        typer.echo(message)

    start_ipython(argv=[], display_banner=False, user_ns=user_ns)
