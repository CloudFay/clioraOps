from dataclasses import replace

import pytest

from clioraOps_cli.core.execution_approval import (
    ApprovalRecord,
    proposal_fingerprint,
)
from clioraOps_cli.core.execution_contracts import ActionProposal


@pytest.fixture
def proposal(tmp_path):
    return ActionProposal(
        command="git status",
        working_directory=str(tmp_path),
    )


def test_fingerprint_is_deterministic(proposal):
    assert proposal_fingerprint(proposal) == proposal_fingerprint(proposal)


def test_approval_record_matches_original_proposal(proposal):
    approval = ApprovalRecord.for_proposal(proposal)

    assert approval.matches(proposal)


@pytest.mark.parametrize(
    "field_changes",
    [
        {"command": "git push origin main"},
        {"working_directory": "different-directory"},
        {"timeout_seconds": 20.0},
        {"max_output_bytes": 8192},
        {"memory_limit_mb": 512},
        {"cpu_limit": 1.5},
        {"network_access": True},
        {"allowed_environment_keys": ("APP_MODE",)},
    ],
)
def test_approval_does_not_match_modified_proposal(
    proposal, field_changes
):
    approval = ApprovalRecord.for_proposal(proposal)
    modified_proposal = replace(proposal, **field_changes)

    assert modified_proposal.proposal_id == proposal.proposal_id
    assert not approval.matches(modified_proposal)


def test_approval_does_not_match_different_proposal_id(proposal):
    approval = ApprovalRecord.for_proposal(proposal)
    different_proposal = replace(proposal, proposal_id="different-id")

    assert not approval.matches(different_proposal)


def test_approval_record_is_immutable(proposal):
    approval = ApprovalRecord.for_proposal(proposal)

    with pytest.raises(AttributeError):
        approval.proposal_id = "changed"


@pytest.mark.parametrize(
    ("proposal_id", "fingerprint"),
    [
        ("", "a" * 64),
        ("proposal-1", "invalid"),
        ("proposal-1", "A" * 64),
    ],
)
def test_invalid_approval_records_are_rejected(proposal_id, fingerprint):
    with pytest.raises(ValueError):
        ApprovalRecord(
            proposal_id=proposal_id,
            proposal_fingerprint=fingerprint,
        )


def test_fingerprint_rejects_non_proposal():
    with pytest.raises(TypeError):
        proposal_fingerprint(None)


def test_approval_does_not_match_non_proposal(proposal):
    approval = ApprovalRecord.for_proposal(proposal)

    assert not approval.matches(None)
