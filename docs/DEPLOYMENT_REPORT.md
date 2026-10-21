# Dionaea deployment audit

Audit date: 2026-10-21 (Europe/London).

## Local quality gate

- 29 Python unit/integration tests pass, including real HTTP requests to all three production entrypoint classes.
- JavaScript syntax and Python compilation checks pass.
- The detector, scenario and evaluation algorithms are unchanged from the AI-assisted starter. Only benchmark file-writing newlines changed for cross-platform byte reproducibility.
- Both benchmark files regenerate byte-for-byte identically to the downloaded source. SHA-256: RESULTS.md `1fc0a1671eac3df5e14316414634dce9bfc0f083d4df936ea80f47cb9e3eb517`; benchmark_results.json `1a907068ab1e6e72f99cdd5f85cf0506250b8588d4032e7c2d00c99beb0007a3`.
- Real Chromium (Edge channel) browser checks pass. See `qa-local.json` for check names and observations.
- At 375, 390, 768, 1024 and 1440 pixels, document scroll width equals viewport width. Tables and chart may scroll inside labelled, keyboard-focusable containers.
- Zero automated WCAG 2 A/AA, 2.1 AA and 2.2 AA violations at those widths. Some color-contrast items require manual review. This is not a claim of full accessibility certification or assistive-technology testing.
- No unexpected browser console errors or HTTP failures in the successful flow. Deliberate QA request failures are exercised separately.
- Desktop and mobile screenshots were inspected, including the home view and mobile laboratory.

## Changes and findings

Added standard-library Vercel Python entrypoints, shared input validation/error handling, security/cache headers, static 404 and safe static routing. Moved canonical frontend from web/ to public/. Added loading, failure/retry, invalid-seed states, cancellation of stale requests, bounded replay inspection, touch/keyboard chart access and synthetic CSV download. Added frozen benchmark results and verified scientific links to the website, truthful project/assistance context, student journal template and push/PR CI.

Fixed low text contrast, missing keyboard focus for the scrolling chart, mouse-only tooltip access, unbounded seed input and future-step tooltip disclosure during replay. Reset cancels replay and pending recalculation. Failed requests clear old scores.

## Production status

Public GitHub and Vercel publishing explicitly approved by the user on 2026-10-21. Production deployment is not yet verified. Verified links, application revision, GitHub Actions/build state, live routes and production-browser results will be recorded after deployment.

## Remaining scientific and QA limits

Synthetic binary signals; subjective costs and cooldown; no physical sensor study or significance test. Delay excludes misses, so interpret it with recall. The student must supply their own dated research contributions. Automated accessibility and emulated touch do not replace screen-reader and physical-device testing. Publisher sites can impose access restrictions even when bibliographic links are correct.
