"""
Input functions

Input functions are always called from the client (they handle server
input, hence the name).

This module is loaded by being included in the
`settings.INPUT_FUNC_MODULES` tuple.

All *global functions* included in this module are considered
input-handler functions and can be called by the client to handle
input.

An input function must have the following call signature:

    cmdname(session, *args, **kwargs)

Where session will be the active session and *args, **kwargs are extra
incoming arguments and keyword properties.

A special command is the "default" command, which is will be called
when no other cmdname matches. It also receives the non-found cmdname
as argument.

    default(session, cmdname, *args, **kwargs)

"""

# import the contents of the default inputhandler_func module
#from evennia.server.inputfuncs import *


# def oob_echo(session, *args, **kwargs):
#     """
#     Example echo function. Echoes args, kwargs sent to it.
#
#     Args:
#         session (Session): The Session to receive the echo.
#         args (list of str): Echo text.
#         kwargs (dict of str, optional): Keyed echo text
#
#     """
#     session.msg(oob=("echo", args, kwargs))
#
#
# def default(session, cmdname, *args, **kwargs):
#     """
#     Handles commands without a matching inputhandler func.
#
#     Args:
#         session (Session): The active Session.
#         cmdname (str): The (unmatched) command name
#         args, kwargs (any): Arguments to function.
#
#     """
#     pass

from athanor.base.handlers import AthanorRequest

def session(source, *args, **kwargs):
    req = AthanorRequest(session=source, handler=args[0], operation=args[1], parameters=kwargs)
    session.ath.accept_request(req)


def account(source, *args, **kwargs):
    req = AthanorRequest(session=source, handler=args[0], operation=args[1], parameters=kwargs)
    session.account.ath.accept_request(req)


def character(source, *args, **kwargs):
    req = AthanorRequest(session=source, handler=args[0], operation=args[1], parameters=kwargs)
    session.puppet.ath.accept_request(req)

def system(source, *args, **kwargs):
    pass