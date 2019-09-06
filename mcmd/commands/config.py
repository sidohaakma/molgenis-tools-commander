import mcmd.config.config as config
import mcmd.io.ask
from mcmd.core.command import command
from mcmd.commands._registry import arguments
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.core.errors import McmdError


# =========
# Arguments
# =========

@arguments('config')
def add_arguments(subparsers):
    p_config = subparsers.add_parser('config',
                                     help='Change the configuration of Molgenis Commander')
    p_config_subparsers = p_config.add_subparsers(dest="type")

    p_config_set = p_config_subparsers.add_parser('set',
                                                  help='Set values in the configuration file')

    p_config_set_subparsers = p_config_set.add_subparsers()
    p_config_set_host = p_config_set_subparsers.add_parser('host',
                                                           help='Select a host')
    p_config_set_host.set_defaults(func=config_set_host,
                                   write_to_history=False)
    p_config_set_host.add_argument('url',
                                   nargs='?',
                                   help='The URL of the host (Optional)')

    p_config_add = p_config_subparsers.add_parser('add',
                                                  help='Add values in the configuration file')
    p_config_add_subparsers = p_config_add.add_subparsers()
    p_config_add_host = p_config_add_subparsers.add_parser('host',
                                                           help='Add a new host')
    p_config_add_host.set_defaults(func=config_add_host,
                                   write_to_history=False)


# =======
# Methods
# =======

@command
def config_set_host(args):
    if args.url:
        url = args.url
    else:
        auths = config.get('host', 'auth')
        urls = [auth['url'] for auth in auths]
        url = mcmd.io.ask.multi_choice('Please select a host:', urls)

    io.start("Switching to host {}".format(highlight(url)))
    config.set_host(url)


@command
# noinspection PyUnusedLocal
def config_add_host(args):
    url = _add_host()
    _switch_to_new_host(url)


def _add_host():
    url = mcmd.io.ask.input_("URL", required=True)
    if config.host_exists(url):
        raise McmdError("A host with URL {} already exists.".format(url))

    username = mcmd.io.ask.input_("Username (Default: admin)")
    password = mcmd.io.ask.password("Password (Leave blank to use command line authentication)")

    username = 'admin' if len(username) == 0 else username
    password = None if len(password) == 0 else password

    io.start("Adding host {}".format(highlight(url)))
    config.add_host(url, username, password)
    io.succeed()
    return url


def _switch_to_new_host(url):
    if mcmd.io.ask.confirm("Do you want to switch to the new host?"):
        io.start("Switching to host {}".format(highlight(url)))
        config.set_host(url)
