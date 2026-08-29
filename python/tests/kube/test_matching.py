"""Unit tests for kube.matching."""

from __future__ import annotations

from kube.matching import match_pods

DEFAULT_ID_PATTERN = r"^[a-z0-9]{10}$"


def _pod(name, timestamp):
    return {"metadata": {"name": name, "creationTimestamp": timestamp}}


def test_match_pods_filters_by_prefix():
    pods = [
        _pod("api-abc1234567", "2024-01-01T00:00:00Z"),
        _pod("worker-abc1234567", "2024-01-01T00:00:00Z"),
    ]

    result = match_pods(pods, "api-", None, DEFAULT_ID_PATTERN)

    assert [p["metadata"]["name"] for p in result] == ["api-abc1234567"]


def test_match_pods_excludes_id_pattern_false_positive():
    # A "my-pod-"-prefixed alias should not match "my-pod-super-<id>", which
    # has an extra "super-" segment the default id_pattern doesn't allow.
    pods = [
        _pod("my-pod-abc1234567", "2024-01-01T00:00:00Z"),
        _pod("my-pod-super-abc1234567", "2024-01-01T00:00:00Z"),
    ]

    result = match_pods(pods, "my-pod-", None, DEFAULT_ID_PATTERN)

    assert [p["metadata"]["name"] for p in result] == ["my-pod-abc1234567"]


def test_match_pods_uses_custom_id_pattern_when_provided():
    pods = [
        _pod("api-123", "2024-01-01T00:00:00Z"),
        _pod("api-abc1234567", "2024-01-01T00:00:00Z"),
    ]

    result = match_pods(pods, "api-", r"^\d+$", DEFAULT_ID_PATTERN)

    assert [p["metadata"]["name"] for p in result] == ["api-123"]


def test_match_pods_falls_back_to_default_id_pattern_when_none():
    pods = [_pod("api-abc1234567", "2024-01-01T00:00:00Z")]

    result = match_pods(pods, "api-", None, DEFAULT_ID_PATTERN)

    assert [p["metadata"]["name"] for p in result] == ["api-abc1234567"]


def test_match_pods_falls_back_to_default_id_pattern_when_falsy():
    pods = [_pod("api-abc1234567", "2024-01-01T00:00:00Z")]

    result = match_pods(pods, "api-", "", DEFAULT_ID_PATTERN)

    assert [p["metadata"]["name"] for p in result] == ["api-abc1234567"]


def test_match_pods_orders_by_creation_timestamp_ascending():
    pods = [
        _pod("api-bbbbbbbbbb", "2024-01-03T00:00:00Z"),
        _pod("api-aaaaaaaaaa", "2024-01-01T00:00:00Z"),
        _pod("api-cccccccccc", "2024-01-02T00:00:00Z"),
    ]

    result = match_pods(pods, "api-", None, DEFAULT_ID_PATTERN)

    assert [p["metadata"]["name"] for p in result] == [
        "api-aaaaaaaaaa",
        "api-cccccccccc",
        "api-bbbbbbbbbb",
    ]
