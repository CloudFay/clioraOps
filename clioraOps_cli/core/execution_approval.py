"""Proposal-bound approval contracts.

These models describe approval records only. They do not establish that
a trusted user approved an action, authorize execution, or provide a
security boundary.
"""

from dataclasses import dataclass
from hashlib import sha256
import json

from clioraOps_cli.core.execution_contracts import ActionProposal


def proposal_fingerprint(proposal: ActionProposal) -> str:
    """Return a deterministic fingerprint of a proposal's contents."""
    if not isinstance(proposal, ActionProposal):
        raise TypeError("proposal must be an ActionProposal")

    payload = {
        "command": proposal.command,
        "working_directory": proposal.working_directory,
        "proposal_id": proposal.proposal_id,
        "timeout_seconds": proposal.timeout_seconds,
        "max_output_bytes": proposal.max_output_bytes,
        "memory_limit_mb": proposal.memory_limit_mb,
        "cpu_limit": proposal.cpu_limit,
        "network_access": proposal.network_access,
        "allowed_environment_keys": list(
            proposal.allowed_environment_keys
        ),
    }

    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    return sha256(canonical_payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ApprovalRecord:
    """Record that references the exact proposal contents reviewed.

    Constructing this record does not prove that approval was obtained
    from a trusted user or authorize execution.
    """

    proposal_id: str
    proposal_fingerprint: str

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")

        if (
            not isinstance(self.proposal_fingerprint, str)
            or len(self.proposal_fingerprint) != 64
            or any(
                character not in "0123456789abcdef"
                for character in self.proposal_fingerprint
            )
        ):
            raise ValueError(
                "proposal_fingerprint must be a lowercase SHA-256 hex digest"
            )

    @classmethod
    def for_proposal(cls, proposal: ActionProposal) -> "ApprovalRecord":
        """Build a record bound to the supplied proposal's current contents."""
        return cls(
            proposal_id=proposal.proposal_id,
            proposal_fingerprint=proposal_fingerprint(proposal),
        )

    def matches(self, proposal: ActionProposal) -> bool:
        """Check whether the record matches this exact proposal."""
        if not isinstance(proposal, ActionProposal):
            return False

        return (
            self.proposal_id == proposal.proposal_id
            and self.proposal_fingerprint == proposal_fingerprint(proposal)
        )
