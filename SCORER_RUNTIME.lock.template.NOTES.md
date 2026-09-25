# Notes on the scorer runtime lock template

`SCORER_RUNTIME.lock.template.json` is schema-valid and deliberately pending: every
field the adapter requires is present, `status` is
`PENDING_CROSS_EVALUATOR_EQUIVALENCE`, and the platform-specific fields are null. A
runtime in this state cannot score. Notes belong here rather than in the template,
because the adapter checks the lock's key set exactly and an extra key would be
rejected as schema drift before the pending status was ever reached.

## repair3

ANIA adapter torch version checks relaxed to PEP 440 public version (both call sites). Proven computationally inert on macOS reference fixtures (byte-identical arrays). Required for Linux execution.
