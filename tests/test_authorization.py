import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from clioraOps_cli.core.authorization import (
    ApprovalAuthority,
    AuthorizationError,
)
from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ApprovalToken,
)


def make_proposal(**overrides):
    values = {
        "command": "git status",
        "working_directory": ".",
    }
    values.update(overrides)
    return ActionProposal(**values)


def test_valid_approval_can_be_consumed_once():
    authority = ApprovalAuthority()
    proposal = make_proposal()

    approval = authority.issue_approval(proposal)

    assert authority.consume_approval(proposal, approval) is None

    with pytest.raises(AuthorizationError):
        authority.consume_approval(proposal, approval)


def test_unknown_token_is_rejected():
    authority = ApprovalAuthority()
    proposal = make_proposal()

    with pytest.raises(AuthorizationError):
        authority.consume_approval(
            proposal,
            ApprovalToken("unknown-token"),
        )


def test_missing_approval_is_rejected():
    authority = ApprovalAuthority()
    proposal = make_proposal()

    with pytest.raises(AuthorizationError):
        authority.consume_approval(proposal, None)


def test_expired_approval_is_rejected():
    now = [100.0]
    authority = ApprovalAuthority(
        ttl_seconds=5,
        clock=lambda: now[0],
    )
    proposal = make_proposal()
    approval = authority.issue_approval(proposal)

    now[0] = 105.0

    with pytest.raises(AuthorizationError, match="expired"):
        authority.consume_approval(proposal, approval)


@pytest.mark.parametrize(
    "changes",
    [
        {"command": "git diff"},
        {"working_directory": "C:/different"},
        {"timeout_seconds": 20.0},
        {"max_output_bytes": 8192},
        {"memory_limit_mb": 512},
        {"cpu_limit": 2.0},
        {"network_access": True},
        {"allowed_environment_keys": ("HOME",)},
    ],
)
def test_changed_proposal_is_rejected(changes):
    authority = ApprovalAuthority()
    proposal = make_proposal()
    approval = authority.issue_approval(proposal)

    changed_proposal = make_proposal(
        proposal_id=proposal.proposal_id,
        **{
            "command": proposal.command,
            "working_directory": proposal.working_directory,
            "timeout_seconds": proposal.timeout_seconds,
            "max_output_bytes": proposal.max_output_bytes,
            "memory_limit_mb": proposal.memory_limit_mb,
            "cpu_limit": proposal.cpu_limit,
            "network_access": proposal.network_access,
            "allowed_environment_keys": proposal.allowed_environment_keys,
            **changes,
        },
    )

    with pytest.raises(AuthorizationError, match="does not match"):
        authority.consume_approval(changed_proposal, approval)


def test_different_proposal_id_is_rejected():
    authority = ApprovalAuthority()
    proposal = make_proposal()
    approval = authority.issue_approval(proposal)

    other_proposal = make_proposal(command=proposal.command)

    with pytest.raises(AuthorizationError, match="does not match"):
        authority.consume_approval(other_proposal, approval)


def test_concurrent_consumption_only_succeeds_once():
    authority = ApprovalAuthority()
    proposal = make_proposal()
    approval = authority.issue_approval(proposal)
    barrier = threading.Barrier(2)

    def attempt():
        barrier.wait()
        try:
            authority.consume_approval(proposal, approval)
            return True
        except AuthorizationError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: attempt(), range(2)))

    assert results.count(True) == 1
    assert results.count(False) == 1


def test_invalid_ttl_is_rejected():
    with pytest.raises(ValueError):
        ApprovalAuthority(ttl_seconds=0)

    with pytest.raises(ValueError):
        ApprovalAuthority(ttl_seconds=-1)

    with pytest.raises(ValueError):
        ApprovalAuthority(ttl_seconds=True)

@pytest.mark.parametrize(
    "ttl_seconds",
    [float("inf"), float("-inf"), float("nan")],
)
def test_non_finite_ttl_is_rejected(ttl_seconds):
    with pytest.raises(ValueError):
        ApprovalAuthority(ttl_seconds=ttl_seconds)
