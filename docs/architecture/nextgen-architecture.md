# ClioraOps Next-Gen Platform Architecture

**Status:** Architecture proposal  
**Last updated:** 2026-10-09  
**Scope:** Incremental evolution of the existing Python CLI into a state-aware DevSecOps learning companion for terminals and IDEs.

## 1. Purpose

ClioraOps is evolving from an AI-assisted DevOps learning CLI into a developer companion that understands the current workspace, explains infrastructure and code, and helps users evaluate operational changes before they act.

The initial approach is a modular Python application. The first milestone is to make workspace context and safety decisions explicit and testable while preserving the existing CLI and AI-provider integrations.

### Goals

- Provide consistent workspace context: project root, detected metadata, relevant tools/configuration, and active task.
- Inspect workspace files using bounded, read-only discovery.
- Keep deterministic policy enforcement independent of AI-generated advice.
- Make risky actions visible, explainable, and subject to explicit authorization.
- Support the current CLI first, then add a Textual terminal UI and later IDE integrations.
- Persist only deliberate, useful workspace/session state with clear storage boundaries.
- Keep implementation status and safety claims auditable through tests and documentation.

### Non-goals for the initial milestone

- Microservices or a remote control plane.
- Automatic execution of arbitrary AI-generated shell commands.
- Running project scripts, package hooks, build systems, or infrastructure plans during discovery.
- Claiming policy review is equivalent to sandboxed execution.
- Storing cloud credentials, access tokens, private keys, or arbitrary environment variables in session state.
- Implementing every IDE integration before core interfaces stabilize.

## 2. Current implementation versus target

| Capability | Status | Current boundary |
| --- | --- | --- |
| Existing CLI and command routing | Implemented | clioraOps_cli/core/commands.py |
| AI provider abstraction and command generation | Implemented | Existing integration and feature modules |
| Deterministic command safety gate | Initial implementation | clioraOps_cli/core/safety_engine.py; conservative allowlist, denial and approval-required outcomes |
| Core command policy manager | Implemented | clioraOps_cli/core/policy.py |
| File/workspace access policy | Implemented | clioraOps_cli/config/policies.py |
| In-memory session context | Partial | clioraOps_cli/core/context.py; several fields are not yet fully maintained |
| Safe workspace discovery | Planned | Must be read-only and bounded |
| Typed, unified workspace model | Planned | Define before adding more discovery behavior |
| Persistent workspace sessions | Planned | Explicit schema, versioning, restrictive storage and secret exclusion |
| Deterministic sandboxed execution | Planned | No general-purpose command execution sandbox exists |
| Textual TUI | Planned | Keep CLI behavior available |
| IDE companion | Planned | Design against stable application interfaces |

**Important:** The safety engine is a decision gate, not a sandbox. ALLOW means a command matches the current limited allowlist; it does not mean the command has been executed or universally proven safe. Unknown commands and shell composition require approval, and the current CLI does not execute the generated shell command.

## 3. Logical architecture

The target is a modular monolith with explicit interfaces. These are logical responsibilities, not a requirement to create a Python package for every box immediately.

    Experience layer
      Existing CLI (implemented) | Textual TUI (planned) | IDE integrations (planned)
                                  |
    Application and orchestration
      Command routing | Use cases | Conversation/session coordination
                                  |
    Workspace intelligence
      Read-only discovery (planned) | Typed workspace context (planned)
      Versioned local session store (planned)
                                  |
    Safety control plane
      Access policies | Deterministic safety engine | Approval workflow (planned)
                                  |
    AI and developer integrations
      AI provider abstraction | Command/code assistance | Review
                                  |
    Controlled action boundary (future; not implemented)
      Isolated execution sandbox (planned) | Audit records (planned)

Experience layers must use the same application services and safety policy. The UI must not become an alternate route around the safety gate.

## 4. Component responsibilities and boundaries

### 4.1 Experience layer

- **CLI — implemented:** retain current commands and existing user workflows.
- **Textual TUI — planned:** present workspace summary, conversation, review findings, and approval prompts without bypassing policy.
- **IDE integrations — planned:** communicate through stable application/use-case interfaces rather than duplicating policy or calling shell commands independently.

### 4.2 Application and orchestration

The application layer coordinates use cases such as inspect workspace, explain a configuration file, generate a proposed command, review a command, and save/restore a session. It should own workflow sequencing, not provider-specific prompts or low-level execution.

Existing clioraOps_cli/core/commands.py is the current entry point. Refactoring should be incremental: extract services when a concrete use case needs them rather than performing a large rewrite up front.

### 4.3 Workspace intelligence

Workspace intelligence will provide a typed context containing, as appropriate:

- Canonical workspace root and current working directory.
- Project type and evidence used to identify it.
- Detected configuration files and relevant metadata.
- Explicitly selected infrastructure context, such as a Kubernetes context/namespace or Terraform workspace, only when safely obtained and clearly labelled.
- Active task and user-confirmed preferences.
- Discovery timestamp, source, and confidence for inferred fields.

Discovery must remain read-only, stay inside the configured workspace boundary unless the user explicitly requests otherwise, enforce file-count/size/depth limits, and avoid following unsafe symlinks. It must not run project-defined commands, scripts, hooks, package managers, Terraform, Kubernetes mutations, or arbitrary binaries to learn about a project.

Unknown or unavailable facts should be represented as unknown rather than guessed. A detected configuration value is not proof that the corresponding cloud or cluster state is current.

### 4.4 Safety control plane

The safety control plane is deterministic and independent of AI output.

- **Access policies:** enforce workspace/path and operation boundaries.
- **Safety engine:** classify a proposed command/action as allowed by the current policy, requiring explicit approval, or denied.
- **Approval workflow — planned:** bind approval to the exact proposed action and relevant context; changes to the action invalidate that approval.
- **Audit trail — planned:** record policy outcome, rationale, action identity, approval and result without recording secrets.

AI may explain a decision but must not override, weaken, or silently bypass it. If policy evaluation fails or context is insufficient, the system should fail closed for actions with side effects.

Current code contains both clioraOps_cli/core/policy.py and clioraOps_cli/config/policies.py. Their responsibilities must be clarified during migration; do not introduce a third overlapping policy implementation. Consolidation should be driven by tests and documented compatibility, not an unreviewed broad rewrite.

### 4.5 AI and developer integrations

AI providers can propose explanations, summaries, code suggestions, or candidate commands. Provider responses are untrusted input and must be schema-validated before use. Deterministic validation and policy checks happen after generation and before any future action.

Provider credentials belong in supported secret/configuration mechanisms and must never be copied into workspace summaries, prompts, logs, or persisted sessions unless a specific, reviewed requirement permits it.

### 4.6 Controlled action boundary

General-purpose command execution and sandboxed execution are **not implemented** by this architecture document. The future action service must be separate from discovery and generation, disabled by default, and reachable only through explicit authorization and policy evaluation.

Before implementation, sandbox design must specify isolation technology, filesystem mounts, network access, resource/time limits, process cleanup, host boundary assumptions, failure handling, and audit records. A container alone must not be described as a complete security boundary without evaluating its configuration and host threat model.

## 5. Key workflows

### 5.1 Workspace inspection

1. Resolve the requested workspace root to a canonical path.
2. Validate that the root is permitted by access policy.
3. Walk only within the allowed root using bounded depth, file count, and file-size limits.
4. Read supported metadata/configuration files without executing their contents.
5. Record evidence, source, and confidence in the workspace model.
6. Redact or skip secret-bearing files and sensitive values.
7. Return a summary and any skipped/unsupported items to the user.

### 5.2 AI-assisted command proposal

1. Receive a user request and relevant, minimized workspace context.
2. Ask the configured provider for a structured proposal.
3. Validate the response shape and extract the proposed command/action.
4. Evaluate it with deterministic safety policy.
5. Explain the outcome and any warnings to the user.
6. Stop on denial or approval-required outcomes. No command is executed by the current workflow.

### 5.3 Future authorized execution

1. Create an immutable action proposal including command, working directory, environment policy, and requested resources.
2. Evaluate it deterministically and deny prohibited actions.
3. Obtain explicit approval for the exact proposal when required.
4. Revalidate the proposal and workspace context before execution.
5. Execute only through the isolated action service with bounded permissions and resources.
6. Capture exit status and sanitized output, write an audit record, and clean up the execution environment.

This workflow is a target design only. Do not implement it by adding a direct subprocess call to the current command router.

### 5.4 Session persistence

1. Construct a versioned, allowlisted session record.
2. Exclude credentials, tokens, private keys, raw environment dumps, and unnecessary file contents.
3. Store it in a user-owned local location with restrictive permissions where supported.
4. Validate schema/version and enforce size limits on load.
5. Treat restored context as stale until revalidated; never restore prior approvals as authorization to execute a future action.

## 6. Trust boundaries and threat assumptions

The platform assumes repository contents, filenames, configuration files, AI output, downloaded templates, and tool output may be malicious or misleading.

| Threat | Required control |
| --- | --- |
| Path traversal or sibling-directory prefix confusion | Canonical path resolution and component-aware containment checks |
| Malicious project files or hooks | Discovery reads metadata only; never executes project content |
| Prompt injection in repository content | Treat file text as untrusted data; it cannot change policy or grant authority |
| AI-generated destructive command | Deterministic deny/approval policy, with no execution by default |
| Shell chaining, redirection, substitution, or remote script piping | Conservative parsing/classification; require approval or deny according to policy |
| Secret leakage through prompts/logs/session files | Minimize context, redact sensitive values, exclude secrets from persistence |
| Stale workspace/session state | Record source/time; revalidate before side-effecting actions |
| Approval reused for a changed command | Bind approval to an exact proposal and invalidate on changes |
| Unsafe template generation or hooks | Treat template acquisition/rendering as a separate threat surface; do not claim it is sandboxed |
| Resource exhaustion during discovery/execution | Enforce file/depth/time/resource limits |

The current regex-based reviewer and conservative command classifier are defense-in-depth, not a complete shell parser or formal safety proof. The project must not claim protection against all dangerous commands.

## 7. Python module direction

Preserve current modules where possible and evolve toward these responsibilities:

| Area | Existing or proposed location | Responsibility |
| --- | --- | --- |
| CLI entry and routing | clioraOps_cli/core/commands.py | Parse and route user requests; delegate use cases |
| Session context | clioraOps_cli/core/context.py | Current in-memory context; evolve toward typed workspace/session models |
| Command safety | clioraOps_cli/core/safety_engine.py | Deterministic classification of proposed commands |
| Core policy | clioraOps_cli/core/policy.py | Existing command/path policy manager; clarify scope |
| Access policy | clioraOps_cli/config/policies.py | File and operation restrictions; clarify overlap with core policy |
| AI integration | Existing provider integration | Provider selection and normalized model calls |
| Workspace discovery | Proposed clioraOps_cli/workspace/ | Read-only discovery and evidence collection |
| Workspace models | Proposed clioraOps_cli/workspace/models.py | Typed workspace/project metadata |
| Session persistence | Proposed clioraOps_cli/sessions/ | Versioned safe serialization and restoration |
| Action isolation | Proposed clioraOps_cli/execution/ | Future sandbox interface; no general execution implementation yet |
| UI | Proposed clioraOps_cli/tui/ | Future Textual experience using application services |

The proposed paths are guidance, not an immediate requirement to create empty packages. Add each module alongside a tested use case.

## 8. Migration plan

### Milestone 1 — Architecture and safety baseline

- Document component boundaries, threat assumptions, and implemented versus planned behavior.
- Keep the existing CLI and provider integrations working.
- Add tests for the deterministic safety gate and path-boundary enforcement.
- Avoid introducing general-purpose shell execution.

### Milestone 2 — Typed workspace context and safe discovery

- Define workspace/project data models and evidence/confidence fields.
- Implement bounded, read-only discovery.
- Test traversal, symlinks, unreadable files, oversized files, secret filtering, and malicious project metadata.
- Keep discovery independent from AI calls and execution.

### Milestone 3 — Persistent sessions

- Define a versioned, allowlisted session schema and storage location.
- Add save/load/migration tests, restrictive permissions where supported, and secret exclusion.
- Treat restored state as untrusted and stale until revalidated.

### Milestone 4 — Safety policy and sandbox design

- Clarify and test the relationship between the two existing policy modules.
- Specify approval semantics and action identity.
- Research isolation options and threat assumptions before implementing any executor.
- Keep execution disabled unless a separate, reviewed feature explicitly enables it.

### Milestone 5 — Textual TUI

- Build a TUI over application services and shared policy.
- Expose workspace state, proposal review, and safety explanations.
- Ensure the TUI cannot bypass CLI/application policy.

### Milestone 6 — IDE integration

- Define a small stable interface for workspace context, assistance, and review.
- Prototype one editor integration only after the underlying service contracts stabilize.
- Keep policy decisions in the core application, not the editor extension.

## 9. Architecture decision records

### ADR-001: Start as a modular monolith

**Decision:** Keep a single Python application with explicit module boundaries.

**Reason:** The current product is a CLI with shared local state and provider integrations. A distributed architecture would add operational complexity before there is a demonstrated need.

**Revisit when:** Independent deployment, scaling, or security boundaries justify a separate service.

### ADR-002: AI proposes; deterministic policy decides

**Decision:** AI output is never the authority for allowing an action.

**Reason:** Model output is variable and may be influenced by untrusted workspace content. Safety decisions need reproducible rules and tests.

### ADR-003: Workspace discovery is read-only

**Decision:** Discovery does not execute project commands, hooks, scripts, or arbitrary binaries.

**Reason:** Inspection must not trigger side effects simply because a user opened a workspace.

### ADR-004: Execution is a separate future capability

**Decision:** Do not add arbitrary shell execution to the command router as part of workspace awareness or UI work.

**Reason:** Execution requires explicit authorization, isolation, resource limits, auditability, and a reviewed threat model.

### ADR-005: Preserve the CLI and migrate incrementally

**Decision:** Keep current user workflows while extracting testable services as needed.

**Reason:** A staged migration lowers regression risk and makes each security-sensitive change reviewable.

### ADR-006: Persist minimal, versioned state

**Decision:** Persist only an explicit allowlist of useful context and never persist secrets or reusable execution approvals.

**Reason:** Local state can become stale or expose sensitive information; schema versioning makes future changes manageable.

## 10. Acceptance criteria for this architecture issue

- [ ] The architecture, responsibilities, and intended module boundaries are documented.
- [ ] Current implementation is clearly distinguished from planned functionality.
- [ ] Workspace discovery and session lifecycle are described.
- [ ] AI generation, deterministic policy, approval, and future execution boundaries are explicit.
- [ ] Threat assumptions and security controls are documented.
- [ ] Migration milestones and decisions are recorded.
- [ ] The document makes no claim that a sandbox, TUI, IDE integration, persistent workspace model, or arbitrary command executor already exists.

## 11. Related work

- Issue #1 — Define the Next-Gen Platform Architecture
- Issue #2 — Implement Deterministic Command Safety Gate
- Issue #3 — Build the State-Aware Workspace Context
- Issue #4 — Implement Safe Workspace Discovery
- Issue #5 — Add Persistent Workspace Sessions
- Issue #6 — Design Deterministic Sandboxed Execution
- Issue #7 — Build the Interactive Terminal UI
- Issue #8 — Plan IDE Integration
- Issue #9 — Publish Technical Specification and Migration Plan

This document establishes the architectural baseline. Follow-up issues should implement the smallest testable increment that conforms to these boundaries.
