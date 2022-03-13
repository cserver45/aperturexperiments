"""Noxfile test template."""
import nox


@nox.session(reuse_venv=True)
def lint(session: nox.Session) -> None:
    """Run flake8, pylint, and pydocstyle on the code."""
    session.install("flake8", "pylint", "pydocstyle")
    session.run("flake8", "--config", "linters.conf", "cogs/", "bot/", "main.py")
    session.run("pylint", "--rcfile", "linters.conf", "--exit-zero", "cogs/", "bot/", "main.py")
    session.run("pydocstyle", "--config", "linters.conf", "cogs/", "bot/", "main.py", success_codes=[0, 2])


@nox.session(reuse_venv=True)
def type_check(session: nox.Session) -> None:
    """Run mypy and static type check the code."""
    session.install("mypy", "types-aiofiles", "types-ujson")
    session.run("mypy", "--config-file", "linters.conf", "cogs/", "bot/", "main.py")


@nox.session(reuse_venv=True)
def reformat_code(session: nox.Session) -> None:
    """Run isort and fix import order."""
    session.install("isort[requirements_deprecated_finder]")
    session.run("isort", "cogs/", "bot/", "main.py")
