# Dionaea production deployment audit

## Learning update verified on 2026-10-22

The public site now includes a twelve-step algorithm walkthrough, exploratory scenario presets, score definitions, detected-only benchmark delay, explanations of each environment's false-alert/recall trade-off and a practical independent-project roadmap. Navigation and mobile settings were refined while retaining the existing botanical laboratory design.

- Application revision: `ea83edf6dbb324fe5e0b221e340f50f3e397b1de`.
- [Successful application CI](https://github.com/mithilkatkoria/dionaea/actions/runs/39694413741).
- Git-triggered production deployment: `dpl_C4Fnd6s2k8aLDcjMYEf7GP9xA8fK`, state READY, owner `mithilkatkoria`.
- 32 Python tests pass, including hand-calculated teaching states, reset behavior and fixture/engine agreement.
- All 23 expanded browser check groups pass locally and against the live URL. The example failure is isolated from the main lab and its retry recovers. Presets preserve the frozen published benchmark.
- All 33 live route/method checks pass, including the new script and generated teaching asset.
- Live HTML, JavaScript, CSS and teaching JSON match the committed source after LF normalization.
- Zero global overflow and zero automated WCAG A/AA violations at 375, 390, 768, 1024 and 1440 pixels. The prior limits on automated accessibility and physical-device coverage still apply.

The teaching sequence is fixed educational input with no truth labels or accuracy claim. `scripts/build_learning_example.py` calls the production Python `detect()` function and writes `public/learning-example.json`; the browser reads its recorded traces. No JavaScript detector implementation was added. It uses cooldown zero to expose each decision, while the main laboratory retains its default shared cooldown of six.

The original detector, generator and evaluator code, published benchmark outputs and train/test split are unchanged. The benchmark regeneration check preserves the exact original SHA-256 hashes recorded below. The new teaching example and website work are Codex-assisted contributions, not an independently conducted student research study. The personal journal remains blank for the student's own work.

Evidence: [browser QA](qa-learning-production.json), [live API QA](qa-learning-api-production.json), [asset comparison](qa-learning-static-production.json), [worked-example screenshot](screenshots/learning-update/worked-example.png), [mobile screenshot](screenshots/learning-update/mobile.png). Screenshots were inspected in the real browser review. This audit is saved in a subsequent documentation-only commit; application files are unchanged by that commit.

## Original launch audit from 2026-10-21

Audit date: 2026-10-21 (Europe/London). Status: verified production deployment.

## Verified destinations

- Public repository: https://github.com/mithilkatkoria/dionaea
- Verified GitHub owner: `mithilkatkoria` (the account without a hyphen).
- Public live laboratory: https://dionaea-seven.vercel.app
- Vercel project: `mithilkatkoria-gmailcoms-projects/dionaea`, in the existing authenticated account.
- Git integration: GitHub repository `mithilkatkoria/dionaea`, production branch `main`.
- Framework: Other (`null`); static output `public`; no install/build command; Python 3.12.
- Audited application revision: `3d9c6b9dbdb02de733df41714de6eb17fae39fb6`.
- Git-triggered Vercel deployment: `dpl_Hp8srug2tNwsMZc5rZV1cVoL68EA`, source `git`, target `production`, state `READY`.
- Application CI: [Quality gate, successful](https://github.com/mithilkatkoria/dionaea/actions/runs/39651420261).

This report and refreshed QA evidence are published in a subsequent documentation-only commit. Application files are unchanged by that commit. The report identifies the exact application revision checked against the live URL, rather than trying to record its own future commit hash.

## Tests and reproducibility

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 29 tests pass, including HTTP requests to the production entrypoint classes |
| `python -m dionaea.benchmark` | All four regimes regenerate reproducibly |
| `python -m scripts.check_reproducibility` | Both published report files are byte-for-byte unchanged |
| `node --check public/main.js` | Pass |
| `python -m compileall -q .` | Pass |
| Chromium browser QA | All 20 check groups pass locally and against production |
| Live API and route audit | All 31 route/method checks pass |
| Deployment asset comparison | Live HTML, JavaScript and CSS match the committed application (LF-normalized) |
| Dependency audit | Browser QA installation reported zero known vulnerabilities |

CI runs on every push and pull request. It runs the Python checks, deterministic benchmark, unchanged-file check, JavaScript syntax check, compilation and the complete browser suite. The Python production runtime has no third-party packages; Node dependencies are development-only QA tools.

Original detector, scenario-generation, evaluation, train/test seeds and benchmark values are retained. Only report file-writing newlines changed to enforce LF on Windows and Linux. Neither held-out tuning nor a new detector was introduced.

SHA-256 of the unchanged downloaded results:

- `experiments/RESULTS.md`: `1fc0a1671eac3df5e14316414634dce9bfc0f083d4df936ea80f47cb9e3eb517`
- `experiments/benchmark_results.json`: `1a907068ab1e6e72f99cdd5f85cf0506250b8588d4032e7c2d00c99beb0007a3`

## Browser, accessibility and viewport observations

The real Chromium browser (installed Edge channel for the local audit) exercised all eight environment/detector sliders, manual/new seeds, reset, replay/pause/completion, pointer/keyboard/touch inspection, published-environment selection and synthetic CSV download. It checked loading, invalid/empty seed, zero observed events with N/A delay, HTTP failure, network failure, request timeout, retry and stale-response cancellation. Restarting replay clears the previously inspected step before any steps are revealed.

At 375, 390, 768, 1024 and 1440 pixels, document scroll width equals viewport width. Desktop uses a settings/sidebar layout. Mobile stacks the settings and analysis with touch-sized playback controls; chart and tables can scroll inside labelled keyboard-focusable containers. The step inspector provides a readable alternative to the chart. Desktop home/laboratory and mobile home/laboratory screenshots were inspected.

Zero automated WCAG 2 A/AA, 2.1 AA and 2.2 AA violations were reported at all five widths. Low-contrast starter labels were darkened and visible keyboard focus was added. Some color-contrast items remain marked for manual review by axe, so these results are not a full accessibility certification. No screen-reader or physical-device testing is claimed.

No unexpected JavaScript console errors or failing HTTP responses were recorded in the successful flow. Deliberate browser-only request failures were separately expected and tested.

Evidence:

- [Local browser results](qa-local.json)
- [Production browser results](qa-production.json)
- [Production API results](qa-api-production.json)
- [Production asset comparison](qa-static-production.json)
- [Desktop laboratory](screenshots/production/desktop.png)
- [Mobile laboratory](screenshots/production/mobile-lab.png)
- [Mobile home](screenshots/production/mobile.png)

## Live routes, errors and caching

| Route or request | Verified response |
| --- | --- |
| `/`, `/index.html`, `/style.css`, `/main.js`, `/favicon.svg`, `/robots.txt` | 200, expected content types |
| `/api/health` | 200, JSON, identifies synthetic data and the four detectors |
| `/api/simulate` | 200; default and modified settings exactly match the local Python engine |
| `/api/benchmark` | 200; exactly matches the saved benchmark JSON |
| Invalid, duplicate, empty, unknown or non-finite simulation parameters | JSON 400 with a useful error |
| POST to the three API endpoints | JSON 405 |
| HEAD to the three API endpoints | 200, no response body |
| Missing route, unknown API, `.env`, `.git/config`, `app.py`, engine source | 404 |

All inspected routes carry security headers, including nosniff, DENY framing and a CSP restricting scripts/network access to this origin. Simulations and health use no-store; static JavaScript/CSS revalidate; benchmark shared caching is consumed by the Vercel edge and the saved data remain unchanged.

The 404 request log contains exactly the six intentional missing/private-source probes, with only paths/methods/statuses retained in [the sanitized log summary](qa-404-log-summary.json). The inspected CDN query for HTTP 500+ returned zero records. The runtime error/fatal query returned zero records in the available five-minute window. A one-hour runtime query exceeded Hobby retention, so that longer period is not claimed as verified.

## Implementation and integrity

The canonical frontend is `public/`. Local `app.py` and the three Vercel `api/` Python entrypoints share `dionaea/http_api.py` and the same detector engine. There is no JavaScript duplicate of the detector logic. Query sizes/values are bounded, private files are not served, and environment files, keys and local Vercel configuration are ignored for Git and deployment uploads.

The website retains the cream/green laboratory design, adds verified scientific sources, frozen held-out results, a synthetic CSV download, explanatory methods and a careful account of the original summer-school visit. It makes no claim of Oxford endorsement, physical plant measurements, novelty, medical suitability or NAB scores.

The README records the real demo, screenshots, quick start, mathematics, actual results, limitations and truthful AI assistance. The research journal template contains dated prompts and blank personal findings. Student ownership must be earned through genuine study and independently documented work. Git history is current and retained.

## Remaining limitations

Synthetic binary signals, subjective costs/cooldown and no physical sensor validation or significance test. Detection delay excludes missed episodes and must be read with recall. Published held-out seeds must not be reused for tuning while still described as untouched tests. Emulated mobile and automated accessibility checks do not replace physical-device or assistive-technology review. Publisher links can impose access restrictions.

No access or approval tasks remain for this deployment.
