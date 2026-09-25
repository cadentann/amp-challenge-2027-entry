# Compute and cost record

Every cloud resource used for this entry, and its disposition. No new money was added, no credits
were bought, no card was charged and Auto-Pay was never enabled. All spend came from the existing
prepaid RunPod balance.

## What ran where

| workload | hardware | cloud | disposition |
|---|---|---|---|
| 50,000-peptide generation (final artifacts) | RTX 4090 | Secure | terminated after evidence recovery |
| Post-promotion end-to-end ×2 (`uv run generate`, byte-identical) | RTX 4090 | Secure | terminated after evidence recovery |
| Linux cross-evaluator equivalence (510,000 values, exact) | CPU | — | terminated |
| Clean-room validation from a fresh clone, unchanged official validator | RTX A4500 | Community | see below |
| Scoring, eligibility, selection, safety screen, homology red team, all analysis | local CPU | — | — |

Eleven pods left idle by earlier phases (505 GB of attached storage, $0.067/hr in aggregate) were
audited against a per-pod evidence-safety manifest and terminated once every artifact they held
was confirmed recovered. That took the standing burn to $0/hr.

## Cost

- Prepaid balance before the clean-room pod: **$9.64**.
- Clean-room pod `ha0leovdwsci49`: **$0.19/hr**, Community cloud, RTX A4500.
- Total cloud spend across the entire final phase: **under three US dollars**.

RunPod's REST API exposes no balance endpoint, so the authoritative figure is the billing page in
the RunPod console. The numbers above are from pod metadata and the balance observed before the
last pod was created.

## Controls that were in place

- An **independent shutdown watchdog** ran outside the session for every GPU pod, polling on a
  fixed interval and issuing a hard `DELETE` at a preset wall-clock deadline regardless of session
  state, with retries and confirmation that the pod was gone. A hung or abandoned session could not
  leave a pod burning.
- Pods were created only on **Community** cloud where the workload permitted it, at the lowest
  offered rate for adequate hardware.
- Evidence was streamed off each pod and hash-verified against its source **before** termination.

## Credential note

A RunPod API key was supplied in the working session to provision and terminate pods. It is
therefore present in that session's transcript. **It should be rotated in the RunPod console now
that the work is finished.** It was stored locally with owner-only permissions and was never
written into this package, the entry repository, or any artifact — verified by scanning the whole
package for credential-shaped strings.

## Final state — nothing is running

The last pod, `ha0leovdwsci49`, ran the clean-room validation and was **terminated** on completion.

  - created ~2026-09-25T18:35Z, terminated 2026-09-25T21:00Z — about 2.4 hours at $0.19/hr, ≈ $0.46
  - the validator itself accounted for 116m37s of that, running two full generation passes
  - confirmed gone: the API returns `{"error":"pod not found","status":404}` for it
  - `GET /v1/pods` returns **0 pods**; total standing burn is **$0.000/hr**
  - the independent shutdown watchdog was stopped after the pod was confirmed terminated

No RunPod resource remains allocated. Nothing further will be charged unless a new pod is created.

## What was never done

No money was added. No credits were bought. Auto-Pay was never enabled. No card was charged. No
new resource was created after the clean-room validation finished.
