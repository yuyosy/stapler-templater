import ipaddress

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from config import TemplateOption
from utilities.resolve_path import resolve_path


def setup_template_environment(option: TemplateOption) -> Environment | None:
    template_folder = resolve_path(option.folder)
    if not template_folder.exists():
        logger.error(f"Template folder does not exist: {template_folder}")
        return None
    if not template_folder.is_dir():
        logger.error(f"Template folder is not a directory: {template_folder}")
        return None

    env = Environment(
        loader=FileSystemLoader(template_folder.as_posix(), encoding=option.encoding)
    )
    setup_filters(env)
    return env


def setup_filters(env: Environment):
    env.filters["ip_address_strict"] = ipaddress.ip_address
    env.filters["ip_network_strict"] = ipaddress.ip_network
    env.filters["ip_interface_strict"] = ipaddress.ip_interface
    env.filters["ip_address"] = ip_address
    env.filters["ip_network"] = ip_network
    env.filters["ip_interface"] = ip_interface
    env.filters["is_ip_address"] = is_ip_address
    env.filters["is_ip_network"] = is_ip_network
    env.filters["is_ip_interface"] = is_ip_interface


def ip_address(value: str) -> str:
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return value


def ip_network(value: str) -> str:
    try:
        return str(ipaddress.ip_network(value))
    except ValueError:
        return value


def ip_interface(value: str) -> str:
    try:
        return str(ipaddress.ip_interface(value))
    except ValueError:
        return value


def is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_ip_network(value: str) -> bool:
    try:
        ipaddress.ip_network(value)
        return True
    except ValueError:
        return False


def is_ip_interface(value: str) -> bool:
    try:
        ipaddress.ip_interface(value)
        return True
    except ValueError:
        return False
