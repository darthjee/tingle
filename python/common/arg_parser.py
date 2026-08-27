#!/usr/bin/env python3
"""
arg_parser.py — Generic, reusable command-line argument parser.

Wraps `argparse.ArgumentParser`, turning a plain list of flag-definition
dicts into a parsed `dict` of option name → value. Command-specific
scripts build their flag list and call `ArgParser(flags).parse()` instead
of building their own `argparse.ArgumentParser`.
"""

from __future__ import annotations

import argparse


class ArgParser:
    """Build and parse command-line arguments from flag definitions."""

    def __init__(self, flags: list[dict]):
        self._flags = flags

    def parse(self, argv: list[str] | None = None) -> dict:
        """Parse argv (defaulting to sys.argv[1:]) and return a dict."""
        namespace = self.build().parse_args(argv)
        return vars(namespace)

    def build(self) -> argparse.ArgumentParser:
        """Build and return the configured argument parser."""
        parser = argparse.ArgumentParser()
        for flag in self._flags:
            kwargs = {k: v for k, v in flag.items() if k != "name"}
            parser.add_argument(flag["name"], **kwargs)
        return parser
