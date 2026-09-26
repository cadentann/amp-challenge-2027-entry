# RunPod credential rotation — procedure, and why I did not do it

## Why

A RunPod API key was supplied in a working chat session so that GPU pods could be provisioned and,
more importantly, reliably terminated. It is therefore present in that session's transcript. Treat it
as **exposed and needing rotation**, regardless of how the transcript is stored.

## Why I did not rotate it

Three reasons, and they are all deliberate:

1. Creating or revoking an API key is an **account-settings change** on your account. That needs your
   explicit approval, and you have not given it for this.
2. The instruction was to rotate it "through a secure workflow" and never let the replacement reach a
   chat session. If I generated the replacement, it would pass through my context — exactly the failure
   mode we are trying to close. The only workflow that actually fixes the exposure is one I am not part
   of.
3. Revoking the key from here would remove the ability to terminate a pod if one were ever left
   running. Nothing is running now (verified: 0 pods, $0.00/hr), so that risk is currently nil — but the
   ordering below still puts revocation after confirmation.

## Procedure

Do this in the RunPod console, not here.

1. **Confirm nothing is running**, so revocation cannot orphan a billable pod.
   Console → Pods should be empty. As of this package: **0 pods, $0.000/hr, balance $7.65**.
2. **Create the replacement first.** Console → Settings → API Keys → *Create API Key*. Give it a
   recognisable name and the narrowest scope that still lets you manage pods.
3. **Store it directly in your password manager.** Copy from the console into the manager. Do not paste
   it into a chat session, a terminal that logs history, a file in this repository, or a note that syncs
   in plaintext.
4. **Revoke the old key.** Same screen → delete the key whose value appeared in the session. Revocation
   is what actually closes the exposure; creating a new key alongside it does nothing on its own.
5. **Confirm the old key is dead.** From a shell, with the *old* value, expect a 401:
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' https://rest.runpod.io/v1/pods \
     -H "Authorization: Bearer <OLD_KEY>"
   ```
   `401` means revoked. `200` means it still works and step 4 did not take effect.
6. **Check billing** for any pod you do not recognise, covering 2026-09-25 to 2026-09-26. Expected
   total for this project's final phase is **about $1.51**: roughly $1.44 on the holdout pod plus
   $0.07 on one that never booted. See `docs/COMPUTE_AND_COST_RECORD.md`.

## What is already verified on our side

- **No credential appears anywhere in this package.** The QA harness scans every file for
  credential-shaped patterns — `rpa_`-prefixed keys, private-key headers, SSH public keys — and it
  passes. Re-run it yourself: `python3 qa/final_qa.py <package-root>`.
- **No credential is in the git repository**, at any commit — the scan covers the working tree, and the
  key was never added to a tracked file.
- The only local copy lived in a session scratchpad with owner-only permissions, outside the project
  tree and outside the release archive. That location is ephemeral and is not part of any deliverable.

## Do not

- Do not send the replacement key to me, or to any chat session, to "verify" it works. Step 5 verifies
  the *old* key is dead, which is the only check that matters and needs no new secret.
- Do not reuse the old key anywhere else on the assumption it is low-value. It can create billable
  resources on your account.
