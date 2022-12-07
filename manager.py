import string
import typer
import functools
from importlib import import_module
from pathlib import Path
from typing import Any


cli = typer.Typer()


def print_error(message: str) -> Any:
    typer.echo(typer.style(message, fg=typer.colors.RED), err=True)


def print_warning(message: str) -> Any:
    typer.echo(typer.style(message, fg=typer.colors.YELLOW), err=True)


def print_success(message: str) -> Any:
    typer.echo(typer.style(message, fg=typer.colors.GREEN))


def _with_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from db import DB

        with DB():
            func(*args, **kwargs)

    return wrapper

def _load_commands_from_path(pkg: str, path: Path) -> None:
    if not path.is_dir():
        return

    for filepath in path.glob("*.py"):
        file = filepath.name
        # 只有以英文字母开头的文件才注册命令, 其他文件忽略(如 `.`, `_` 等开头的文件)
        if file[0] not in string.ascii_letters:
            continue
        command_name = file[:-3]
        try:
            module = import_module(f"{pkg}.{command_name}")
            if not hasattr(module, "command"):
                typer.echo(
                    typer.style(
                        f"Warning: {pkg}.{command_name} 没有定义 command() 函数",
                        fg=typer.colors.RED,
                    )
                )
            else:
                command_func = getattr(module, "command")
                cli.command(command_name)(command_func)
        except ModuleNotFoundError as e:
            typer.echo(e)
            pass

def populate_application_commands():
    # _load_commands_from_path("fastframe.fastapp.commands", Path(__file__).parent)
    _load_commands_from_path("commands", Path(__file__).parent / "commands")


populate_application_commands()


if __name__ == "__main__":
    cli()
