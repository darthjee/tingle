"""The container output sample from the spec (subcommand.md §5), shared by tests."""

from __future__ import annotations

import copy
import json

SAMPLE: dict = {
    "metadata": {"rubycritic": {"version": "5.0.0"}},
    "analysed_modules": [
        {
            "name": "Complex",
            "path": "complex.rb",
            "smells": [
                {
                    "context": "Complex#run",
                    "cost": 0,
                    "locations": [{"path": "complex.rb", "line": 2}],
                    "message": "has a flog score of 72",
                    "score": 72,
                    "status": "new",
                    "type": "VeryHighComplexity",
                },
                {"context": "Complex#run", "type": "TooManyStatements"},
                {"context": "Complex#run", "type": "UncommunicativeVariableName"},
            ],
            "churn": 0,
            "committed_at": None,
            "complexity": 72.25,
            "duplication": 0,
            "methods_count": 1,
            "cost": 2.89,
            "rating": "B",
        },
        {
            "name": "DupA",
            "path": "dup_a.rb",
            "smells": [
                {
                    "context": "Identical code",
                    "cost": 6,
                    "locations": [
                        {"path": "dup_a.rb", "line": 2},
                        {"path": "dup_b.rb", "line": 2},
                    ],
                    "message": "found in 2 nodes",
                    "score": 156,
                    "status": "new",
                    "type": "DuplicateCode",
                },
                {"context": "DupA#a", "type": "HighComplexity"},
                {"context": "DupA#a", "type": "FeatureEnvy"},
            ],
            "churn": 0,
            "committed_at": None,
            "complexity": 15.11,
            "duplication": 39,
            "methods_count": 1,
            "cost": 6.6044,
            "rating": "C",
        },
        {
            "name": "Empty",
            "path": "empty.rb",
            "smells": [],
            "churn": 0,
            "committed_at": None,
            "complexity": 0.0,
            "duplication": 0,
            "methods_count": 0,
            "cost": 0.0,
            "rating": "A",
        },
    ],
    "score": 83.23,
    "parse_errors": [{"path": "broken.rb", "message": "unexpected token tSTRING"}],
    "methods": [
        {"path": "complex.rb", "name": "Complex#run", "line": 2, "score": 72.25},
        {"path": "dup_a.rb", "name": "DupA#a", "line": 2, "score": 15.11},
    ],
}

SENT = ["broken.rb", "complex.rb", "dup_a.rb", "empty.rb"]


def sample(**changes) -> dict:
    """Return a deep copy of SAMPLE with top-level `changes` applied."""
    data = copy.deepcopy(SAMPLE)
    data.update(changes)
    return data


def dumps(data: dict | None = None) -> str:
    """Serialise `data` (default: SAMPLE) as the container would."""
    return json.dumps(SAMPLE if data is None else data)
