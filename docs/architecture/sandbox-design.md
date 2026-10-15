# ClioraOps Sandboxed Execution Design

**Status:** Proposed — design only
**Scope:** Define the security contract for future isolated command testing. No command executor is implemented by this document.

## 1. Goals and non-goals

### Goals
- Define a controlled, disposable environment for testing approved command proposals.
- Keep command generation, policy evaluation, approval, execution, and auditing separate.
- Bound filesystem access, network access, runtime, and resource consumption.
- Make failures, timeouts, and cleanup outcomes explicit and testable.

### Non-goals
- Automatically execute arbitrary AI-generated commands.
- Run commands against production infrastructure.
- Treat the existing safety engine or a container as a complete security boundary.
- Enable execution through the current command router.

## 2. Proposed architecture

The future execution workflow consists of:

1. Create an immutable action proposal.
2. Validate its schema and requested resources.
3. Evaluate the proposal using deterministic policy.
4. Obtain explicit approval where required, bound to the exact proposal.
5. Revalidate the proposal and relevant workspace state.
6. Execute through an isolated adapter with bounded permissions.
7. Capture bounded output and the exit status.
8. Write a sanitized audit record.
9. Terminate the workload and clean up temporary resources.

Execution remains disabled by default. Policy errors, invalid requests, and missing required authorization fail closed.

## 3. Component boundaries

- **Command safety engine:** Classifies proposed commands; does not execute them.
- **Access policy:** Controls permitted paths and operations.
- **Action proposal:** Identifies the exact command, working directory, environment policy, and resource limits.
- **Approval service:** Authorizes a specific proposal; any material change invalidates approval.
- **Sandbox executor:** Provides a narrow interface for isolated execution.
- **Execution adapter:** Implements the chosen isolation technology.
- **Audit service:** Records decisions and execution outcomes without exposing secrets.

Clarify the responsibilities of `core/policy.py` and `config/policies.py` before integrating these components. Do not add a third overlapping policy manager.

## 4. Isolation technology

Docker is a candidate for the first execution adapter, subject to threat-model review and secure configuration.

The design must evaluate:

- Host and container boundary assumptions.
- Rootless operation where practical, non-root execution, and dropped capabilities.
- Pinned images and controlled image provenance.
- A read-only base filesystem where possible.
- A dedicated temporary workspace with narrowly scoped mounts.
- No Docker socket, host credentials, or unrelated host directories.
- Network access disabled by default.
- CPU, memory, process-count, output-size, and wall-clock limits.
- Process termination and resource cleanup after completion or failure.

A container reduces exposure but does not guarantee protection against host compromise. Stronger isolation may be required for hostile workloads.

## 5. Filesystem and workspace policy

Only explicitly selected input files should be made available to a test run. Avoid broad host mounts and writable access to the original project.

Resolve and validate paths before preparing inputs. Account for symlinks, traversal, temporary files, and path changes between approval and execution.

Use disposable output locations. Copy results back only through a separately validated, explicitly authorized operation.

## 6. Network and secrets

Network access is denied by default. Any future exception must be narrow, explicit, and reviewed.

Do not pass cloud credentials, SSH keys, host environment dumps, provider tokens, or unrelated secrets into the execution environment. Do not expose the container runtime socket.

Treat command output and generated files as untrusted data.

## 7. Resource limits and failure handling

Enforce configurable limits for execution duration, memory, CPU, process count, captured output, and temporary storage.

Represent success, non-zero exit, timeout, cancellation, policy denial, infrastructure failure, and cleanup failure distinctly.

Do not report successful cleanup unless it has been confirmed. Failed or incomplete cleanup must be recorded and surfaced to the caller.

## 8. Approval and audit

Approval must bind to the exact action proposal, including the command, working directory, environment policy, requested resources, and relevant execution configuration.

Revalidate the proposal immediately before execution. Do not restore approvals from saved sessions.

Audit records should contain a proposal identifier, policy decision, approval status, execution adapter and image identity, timestamps, exit status, timeout state, and cleanup outcome. Exclude credentials and sensitive output.

## 9. Threat model and limitations

Assume commands, repository content, AI responses, configuration files, and execution output may be malicious.

Consider container escape, resource exhaustion, filesystem exposure, network exfiltration, stale approval, policy disagreement, runtime failure, and secret leakage.

The existing regex-based command classifier is defense-in-depth, not a complete shell parser or a guarantee that an action is safe.

## 10. Proposed implementation sequence

1. Review and document policy ownership.
2. Define typed action proposal and execution result models.
3. Define a sandbox executor interface and test its contract without executing commands.
4. Select an isolation backend based on the threat model and supported platforms.
5. Implement bounded execution behind an explicit feature flag, disabled by default.
6. Add tests for denied actions, approval binding, limits, timeouts, output bounds, cleanup, and failure handling.
7. Conduct a security review before enabling execution for users.

## 11. Acceptance criteria

- Isolation options and threat assumptions are documented.
- Filesystem, network, credential, and resource boundaries are explicit.
- Approval and audit semantics are defined.
- Policy ownership and the two existing policy modules are addressed.
- Failure handling and cleanup requirements are specified.
- No arbitrary command execution is introduced into the current CLI.
- No claim is made that sandboxed execution already exists.
