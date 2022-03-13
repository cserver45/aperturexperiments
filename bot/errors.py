"""Exceptions used throughout the bot."""


class InvalidToken(Exception):
    """Exception that is thrown when there is a invalid token type provided in the arguments when starting up."""


class CommandError(Exception):
    """Thrown when a error is raised with any command that is not a CommandNotFound (discord.errors.CommandNotFound)."""
