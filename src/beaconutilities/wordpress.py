"""WordPress REST API client for BeaconUtilities.

Publishes and updates WordPress posts using HTTP Basic Authentication with an
application password.  Supports configurable post types so members and groups
can be targeted at different content types.
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin

import requests

log = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds


class WordPressClient:
    """Thin wrapper around the WordPress REST API ``/wp/v2`` namespace.

    Args:
        site_url: Base URL of the WordPress site, e.g. ``https://example.com``.
        username: WordPress username.
        application_password: Application password generated in WP Admin.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        site_url: str,
        username: str,
        application_password: str,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base = site_url.rstrip("/") + "/wp-json/wp/v2/"
        self._auth = (username, application_password)
        self._timeout = timeout
        self._session = requests.Session()
        self._session.auth = self._auth
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upsert_post(self, payload: dict, post_type: str = "posts") -> dict:
        """Create or update a WordPress post, using ``slug`` as the idempotency key.

        If a post with the given slug already exists it is updated (PUT),
        otherwise a new post is created (POST).

        Args:
            payload: WordPress REST API payload dict.  Must include a
                     ``"slug"`` key for idempotency lookup.
            post_type: REST API resource name, e.g. ``"posts"``, ``"pages"``,
                       or a custom post type slug like ``"members"``.

        Returns:
            The WordPress API response body as a dict.

        Raises:
            requests.HTTPError: On non-2xx responses.
            KeyError: If ``payload`` does not contain a ``"slug"`` key.
        """
        slug = payload["slug"]
        existing = self.find_by_slug(slug, post_type=post_type)
        if existing:
            post_id = existing["id"]
            log.info("Updating existing %s post id=%s slug=%s", post_type, post_id, slug)
            return self._put(post_type, post_id, payload)
        log.info("Creating new %s post slug=%s", post_type, slug)
        return self._post(post_type, payload)

    def find_by_slug(self, slug: str, post_type: str = "posts") -> dict | None:
        """Return the first post matching *slug*, or ``None`` if not found.

        Args:
            slug: WordPress post slug to search for.
            post_type: REST API resource name.

        Returns:
            Post dict from the API, or ``None``.

        Raises:
            requests.HTTPError: On non-2xx responses.
        """
        url = urljoin(self._base, post_type)
        response = self._session.get(
            url,
            params={"slug": slug, "status": "any", "_fields": "id,slug,title"},
            timeout=self._timeout,
        )
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post(self, post_type: str, payload: dict) -> dict:
        url = urljoin(self._base, post_type)
        response = self._session.post(url, json=payload, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def _put(self, post_type: str, post_id: int, payload: dict) -> dict:
        url = urljoin(self._base, f"{post_type}/{post_id}")
        response = self._session.put(url, json=payload, timeout=self._timeout)
        response.raise_for_status()
        return response.json()


def client_from_config(config: dict) -> WordPressClient:
    """Construct a :class:`WordPressClient` from the loaded configuration dict.

    Args:
        config: Dict produced by :func:`beaconutilities.config.load_config`.
                Must contain a ``[wordpress]`` section with ``site_url``,
                ``username``, and ``application_password``.

    Returns:
        Configured :class:`WordPressClient` instance.
    """
    wp = config["wordpress"]
    return WordPressClient(
        site_url=wp["site_url"],
        username=wp["username"],
        application_password=wp["application_password"],
    )
