# -*- coding: utf-8 -*-
# requires a recent enough python with idna support in socket
# pyopenssl, cryptography and idna
import socket
import ssl
from collections import namedtuple
from datetime import datetime

import idna
from cryptography import x509
from cryptography.x509.oid import NameOID
from OpenSSL import SSL

HostInfo = namedtuple(field_names="cert hostname peername", typename="HostInfo")


def has_expired(not_before, not_after):
    # verify notAfter/notBefore, CA trusted, servername/sni/hostname
    start = datetime.strptime(not_before, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(not_after, "%Y-%m-%d %H:%M:%S")
    return start < datetime.now() < end
    # service_identity.pyopenssl.verify_hostname(client_ssl, hostname)
    # issuer


# The PyOpenSSL library doesn't have a (working) way of setting
# the socket timeout and will wait for 300 seconds before timing out.
# This helper function just checks to see if it can make an SSL
# connection before the rest of the get_certificate method runs.
def check_if_ssl(hostname, port):
    valid = True
    _ssl_ctx = ssl.SSLContext()
    _ssl_ctx.verify_mode = ssl.CERT_NONE
    _ssl_ctx.check_hostname = False
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.settimeout(5)
    _ssl_sock = _ssl_ctx.wrap_socket(_sock, do_handshake_on_connect=False)
    try:
        _ssl_sock.connect((hostname, port))
        _ssl_sock.do_handshake()
    except Exception as e:
        valid = False
    finally:
        _ssl_sock.close()
    return valid


def get_certificate(hostname, port):
    if not check_if_ssl(hostname, port):
        raise TimeoutError(f"Failed to make SSL connection to {hostname}")

    hostname_idna = idna.encode(hostname)
    sock = socket.socket()

    sock.connect((hostname, port))
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.SSLv23_METHOD)  # most compatible
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()
    sock_ssl.close()
    sock.close()

    return HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)


def get_alt_names(cert):
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return None


def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def print_basic_info(hostinfo):
    s = """» {hostname} « … {peername}
    \tcommonName: {commonname}
    \tSAN: {SAN}
    \tissuer: {issuer}
    \tnotBefore: {notbefore}
    \tnotAfter:  {notafter}
    \texpired: {expired}
    """.format(
        hostname=hostinfo.hostname,
        peername=hostinfo.peername,
        commonname=get_common_name(hostinfo.cert),
        SAN=get_alt_names(hostinfo.cert),
        issuer=get_issuer(hostinfo.cert),
        notbefore=hostinfo.cert.not_valid_before,
        notafter=hostinfo.cert.not_valid_after,
        expired=not (
            hostinfo.cert.not_valid_before
            < datetime.now()
            < hostinfo.cert.not_valid_after
        ),
    )
    print(s)


def check_it_out(hostname, port):
    hostinfo = get_certificate(hostname, port)
    print_basic_info(hostinfo)


if __name__ == "__main__":
    hostinfo = get_certificate("www.viatel.com", 443)
    print_basic_info(hostinfo)
