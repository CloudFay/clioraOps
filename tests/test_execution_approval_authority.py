from dataclasses import replace

from clioraOps_cli.core.execution_approval import ApprovalRecord
from clioraOps_cli.core.execution_approval_authority import (
    ProcessLocalApprovalAuthority,
)
from clioraOps_cli.core.execution_approval_workflow import ApprovalDecision
from clioraOps_cli.core.execution_contracts import ActionProposal
from clioraOps_cli.core.execution_policy import (
    ExecutionDecision,
    PolicyEvaluation,
)


def make_proposal(tmp_path):
    return ActionProposal(
        command="echo hello",
        working_directory=str(tmp_path),
    )


def make_evaluation():
    return PolicyEvaluation(
        decision=ExecutionDecision.ALLOW,
        reason="Allowed for this test.",
    )


def test_explicit_approval_can_be_verified_once(tmp_path):
    proposal = make_proposal(tmp_path)
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: f"approve {proposal.proposal_id}",
        output_fn=lambda _: None,
    )

    decision = authority.decide(proposal, make_evaluation())
    record = ApprovalRecord.for_proposal(proposal)

    assert decision is ApprovalDecision.APPROVE
    assert authority.verify(proposal, record) is True
    assert authority.verify(proposal, record) is False


def test_rejection_does_not_create_verifiable_approval(tmp_path):
    proposal = make_proposal(tmp_path)
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: f"reject {proposal.proposal_id}",
        output_fn=lambda _: None,
    )

    assert authority.decide(proposal, make_evaluation()) is ApprovalDecision.REJECT
    assert authority.verify(
        proposal,
        ApprovalRecord.for_proposal(proposal),
    ) is False


def test_incorrect_confirmation_fails_closed(tmp_path):
    proposal = make_proposal(tmp_path)
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: "approve wrong-id",
        output_fn=lambda _: None,
    )

    assert authority.decide(proposal, make_evaluation()) is ApprovalDecision.REJECT


def test_modified_proposal_cannot_use_original_approval(tmp_path):
    proposal = make_proposal(tmp_path)
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: f"approve {proposal.proposal_id}",
        output_fn=lambda _: None,
    )

    authority.decide(proposal, make_evaluation())
    record = ApprovalRecord.for_proposal(proposal)
    modified = replace(proposal, command="echo changed")

    assert authority.verify(modified, record) is False
    assert authority.verify(proposal, record) is True


def test_expired_approval_is_rejected(tmp_path):
    proposal = make_proposal(tmp_path)
    current_time = [100.0]
    authority = ProcessLocalApprovalAuthority(
        approval_ttl_seconds=5,
        input_fn=lambda _: f"approve {proposal.proposal_id}",
        output_fn=lambda _: None,
        clock=lambda: current_time[0],
    )

    authority.decide(proposal, make_evaluation())
    record = ApprovalRecord.for_proposal(proposal)
    current_time[0] = 105.0

    assert authority.verify(proposal, record) is False
    assert authority.verify(proposal, record) is False


def test_approval_displays_proposal_details(tmp_path):
    proposal = make_proposal(tmp_path)
    output = []
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: f"reject {proposal.proposal_id}",
        output_fn=output.append,
    )

    authority.decide(proposal, make_evaluation())

    displayed = "\n".join(output)
    assert proposal.command in displayed
    assert proposal.working_directory in displayed
    assert proposal.proposal_id in displayed
    assert "No command has been executed." in displayed


def test_invalid_expiration_is_rejected():
    import pytest

    for invalid_ttl in (0, -1, float("inf"), float("nan"), True):
        with pytest.raises(ValueError):
            ProcessLocalApprovalAuthority(
                approval_ttl_seconds=invalid_ttl,
            )


def test_repeated_approval_does_not_extend_expiration(tmp_path):
    proposal = make_proposal(tmp_path)
    current_time = [100.0]

    authority = ProcessLocalApprovalAuthority(
        approval_ttl_seconds=5,
        input_fn=lambda _: f"approve {proposal.proposal_id}",
        output_fn=lambda _: None,
        clock=lambda: current_time[0],
    )

    evaluation = make_evaluation()

    assert authority.decide(proposal, evaluation) is ApprovalDecision.APPROVE

    current_time[0] = 104.0
    assert authority.decide(proposal, evaluation) is ApprovalDecision.APPROVE

    record = ApprovalRecord.for_proposal(proposal)
    current_time[0] = 105.0

    assert authority.verify(proposal, record) is False
