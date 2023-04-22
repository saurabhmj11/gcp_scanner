import logging
import os
import sys
from typing import Dict, List, Mapping, Optional, Tuple, Union

import requests
from google.auth import credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account


CREDENTIALS_DB_SEARCH_PLACES = ['/home/', '/root/']


def credentials_from_token(
    access_token: str,
    refresh_token: Optional[str],
    token_uri: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str],
    scopes_user: Optional[str],
) -> credentials.Credentials:
    return credentials.Credentials(
        access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes_user,
    )


def get_creds_from_file(file_path: str) -> Tuple[str, credentials.Credentials]:
    """Creates a Credentials instance from a service account JSON file.

    Args:
        file_path: The path to the service account JSON file.

    Returns:
        Tuple[str, google.auth.service_account.Credentials]: The email address associated with
        a service account and the constructed credentials.
    """
    logging.info(f"Retrieving credentials from {file_path}")
    creds = service_account.Credentials.from_service_account_file(file_path)
    return creds.service_account_email, creds


def get_creds_from_json(parsed_keyfile: Mapping[str, str]) -> credentials.Credentials:
    """Creates a Credentials instance from parsed service account information.

    Args:
        parsed_keyfile: The service account information in Google format.

    Returns:
        google.auth.service_account.Credentials: The constructed credentials.
    """
    return service_account.Credentials.from_service_account_info(parsed_keyfile)


def get_creds_from_metadata() -> Tuple[Optional[str], Optional[credentials.Credentials]]:
    """Retrieves a Credentials instance from compute instance metadata.

    Returns:
        Tuple[Optional[str], Optional[google.auth.service_account.Credentials]]: The email
        associated with the credentials and the constructed credentials.
    """
    print("Retrieving access token from instance metadata")

    token_url = (
        "http://metadata.google.internal/computeMetadata/v1/instance/"
        "service-accounts/default/token"
    )
    scope_url = (
        "http://metadata.google.internal/computeMetadata/v1/instance/"
        "service-accounts/default/scopes"
    )
    email_url = (
        "http://metadata.google.internal/computeMetadata/v1/instance/"
        "service-accounts/default/email"
    )
    headers = {"Metadata-Flavor": "Google"}
    try:
        res = requests.get(token_url, headers=headers)
        res.raise_for_status()
        token = res.json()["access_token"]

        res = requests.get(scope_url, headers=headers)
        res.raise_for_status()
        instance_scopes = res.content.decode("utf-8")

        res = requests.get(email_url, headers=headers)
        res.raise_for_status()
        email = res.content.decode("utf-8")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve instance metadata: {e}")
        return None, None

    print("Successfully retrieved instance metadata")
    logging.info(f"Access token length: {len(token)}")
    logging.info(f"Instance email: {email}")
    logging.info(f"Instance scopes: {instance_scopes}")
    return email, credentials_from_token(token, None, None, None, None, instance_scopes)


def get_creds_from_data(
    access_token: str, parsed_keyfile: Dict[str, str]
) -> credentials.Credentials:
    """Creates a Credentials instance from
