import ipaddress
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit


DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.IGNORECASE,
)


class UnsafeTargetError(ValueError):
    pass


@dataclass(frozen=True)
class NormalizedTarget:
    original: str
    domain: str
    was_url: bool


def _normalize_hostname(value: str) -> str:
    hostname = value.strip().rstrip(".").lower()
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise ValueError("Introduce un nombre de dominio, no una dirección IP directa.")
    try:
        ascii_domain = hostname.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("El dominio internacionalizado no es válido.") from exc
    if not DOMAIN_PATTERN.fullmatch(ascii_domain):
        raise ValueError("El formato del dominio no es válido.")
    return ascii_domain


def normalize_target(raw_target: str) -> NormalizedTarget:
    value = raw_target.strip()
    if not value:
        raise ValueError("Introduce un dominio o una URL.")

    if "://" in value:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("Solo se admiten URLs con protocolo HTTP o HTTPS.")
        if parsed.username or parsed.password:
            raise ValueError("No se admiten credenciales en la URL.")
        try:
            if parsed.port is not None:
                raise ValueError("No se admiten puertos personalizados en la URL.")
        except ValueError as exc:
            if "Port could not" in str(exc):
                raise ValueError("El puerto de la URL no es válido.") from exc
            raise
        if not parsed.hostname:
            raise ValueError("La URL no contiene un dominio válido.")
        return NormalizedTarget(
            original=value,
            domain=_normalize_hostname(parsed.hostname),
            was_url=True,
        )

    if any(char in value for char in "/?#@"):
        raise ValueError(
            "Usa un dominio sin ruta o una URL completa con http:// o https://."
        )
    return NormalizedTarget(
        original=value,
        domain=_normalize_hostname(value),
        was_url=False,
    )


def normalize_domain(raw_domain: str) -> str:
    """Compatibilidad con llamadas internas y tests de la versión 0.1."""

    return normalize_target(raw_domain).domain


def is_public_ip(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return address.is_global


async def resolve_public_ips(domain: str) -> list[str]:
    loop = __import__("asyncio").get_running_loop()
    try:
        rows = await loop.getaddrinfo(domain, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("El dominio no resuelve a ninguna dirección IP.") from exc

    addresses = sorted({row[4][0] for row in rows})
    if not addresses:
        raise ValueError("El dominio no resuelve a ninguna dirección IP.")
    blocked = [address for address in addresses if not is_public_ip(address)]
    if blocked:
        raise UnsafeTargetError(
            "El destino resuelve a una red privada, local o reservada y se ha bloqueado."
        )
    return addresses
