"""Tests for beaconutilities.wordpress.WordPressClient."""

from __future__ import annotations

import pytest
import requests

from beaconutilities.wordpress import WordPressClient, client_from_config


@pytest.fixture()
def client():
    return WordPressClient(
        site_url="https://wp.example.com",
        username="user",
        application_password="pass",
    )


class TestClientFromConfig:
    def test_creates_client(self, minimal_config):
        c = client_from_config(minimal_config)
        assert isinstance(c, WordPressClient)

    def test_raises_on_missing_wordpress_section(self):
        with pytest.raises(KeyError):
            client_from_config({})


class TestFindBySlug:
    def test_returns_post_when_found(self, client, requests_mock):
        requests_mock.get(
            "https://wp.example.com/wp-json/wp/v2/posts",
            json=[{"id": 1, "slug": "member-1001", "title": {"rendered": "Alice"}}],
        )
        result = client.find_by_slug("member-1001")
        assert result["id"] == 1

    def test_returns_none_when_not_found(self, client, requests_mock):
        requests_mock.get(
            "https://wp.example.com/wp-json/wp/v2/posts",
            json=[],
        )
        assert client.find_by_slug("no-such-slug") is None

    def test_raises_on_http_error(self, client, requests_mock):
        requests_mock.get(
            "https://wp.example.com/wp-json/wp/v2/posts",
            status_code=401,
        )
        with pytest.raises(requests.HTTPError):
            client.find_by_slug("slug")


class TestUpsertPost:
    def test_creates_when_not_existing(self, client, requests_mock):
        requests_mock.get(
            "https://wp.example.com/wp-json/wp/v2/posts",
            json=[],
        )
        requests_mock.post(
            "https://wp.example.com/wp-json/wp/v2/posts",
            json={"id": 99, "slug": "member-1001"},
            status_code=201,
        )
        result = client.upsert_post(
            {"slug": "member-1001", "title": "Alice", "status": "publish"}
        )
        assert result["id"] == 99

    def test_updates_when_existing(self, client, requests_mock):
        requests_mock.get(
            "https://wp.example.com/wp-json/wp/v2/posts",
            json=[{"id": 7, "slug": "member-1001"}],
        )
        requests_mock.put(
            "https://wp.example.com/wp-json/wp/v2/posts/7",
            json={"id": 7, "slug": "member-1001"},
        )
        result = client.upsert_post(
            {"slug": "member-1001", "title": "Alice Updated", "status": "publish"}
        )
        assert result["id"] == 7

    def test_raises_without_slug(self, client):
        with pytest.raises(KeyError):
            client.upsert_post({"title": "No Slug"})

    def test_raises_on_post_http_error(self, client, requests_mock):
        requests_mock.get(
            "https://wp.example.com/wp-json/wp/v2/posts",
            json=[],
        )
        requests_mock.post(
            "https://wp.example.com/wp-json/wp/v2/posts",
            status_code=403,
        )
        with pytest.raises(requests.HTTPError):
            client.upsert_post({"slug": "test", "title": "T", "status": "publish"})
