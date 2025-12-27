# Security and Threat Model

This project handles player saves, third-party plugins, and user-supplied assets. The following threats are in scope:

- **Path traversal and arbitrary file writes** via crafted save-slot names or asset filenames.
- **Resource exhaustion** from oversized payloads or plugins that loop forever.
- **Malicious code execution** inside community mods that attempt to access the filesystem or sensitive APIs.

## Mitigations

- Save slots and asset ingest paths are validated to reject traversal attempts and only allow safe characters, ensuring writes stay inside dedicated directories.
- Payloads for saves, metadata, and assets are size-checked with configurable byte caps to prevent memory exhaustion or disk abuse.
- Plugins are executed through a sandboxed loader that restricts builtins, only permits a small import allowlist, enforces memory limits, and uses subprocess timeouts to terminate runaway code.
- Validation failures raise explicit errors so the calling layer can surface actionable messages without partially written data.

## Usage Guidance

- Keep plugin directories isolated from the main game data to benefit from the sandbox's path checks.
- Lower the payload and memory limits further when running in constrained or multi-tenant environments.
- Treat sandbox errors as security signals; do not bypass the guardrails to "force" a plugin to run.
