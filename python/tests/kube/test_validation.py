"""Unit tests for kube.validation."""

from __future__ import annotations

import pytest

from kube.validation import is_valid_resource_name


@pytest.mark.parametrize("value", ["default", "api-abc1234567"])
def test_is_valid_resource_name_accepts_valid_names(value):
    assert is_valid_resource_name(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Default",
        "-default",
        "default-",
        "--kubeconfig=/tmp/evil",
    ],
)
def test_is_valid_resource_name_rejects_invalid_names(value):
    assert is_valid_resource_name(value) is False


def test_is_valid_resource_name_rejects_value_over_max_length():
    assert is_valid_resource_name("a" * 254) is False


def test_is_valid_resource_name_respects_custom_max_length():
    assert is_valid_resource_name("a" * 63, max_length=63) is True
    assert is_valid_resource_name("a" * 64, max_length=63) is False
