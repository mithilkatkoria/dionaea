# Publishing and verification checklist

This project is synthetic, initially AI-assisted and independent of Oxford. Preserve that attribution in any presentation.

- Run all Python unit/integration tests, JavaScript syntax and Python compilation checks.
- Rerun the deterministic benchmark. Compare both output files byte-for-byte using `python -m scripts.check_reproducibility`.
- Preserve the original detectors, train/test split and subjective cost definition unless a change is explicitly documented and every affected result regenerated.
- Use `public/` as the frontend, three `api/` Python functions, shared `dionaea/` logic and framework Other on Vercel.
- Inspect the Git diff and staged paths for credentials, personal datasets and local configuration before publishing.
- Publish in the connected user's own GitHub account. Keep a truthful current contribution history.
- Configure CI on every push and pull request. Wait for the exact published commit to pass.
- Connect the repository to the user's Vercel account. Verify a Git-triggered production build.
- Inspect the deployed site in a real browser at 375, 390, 768, 1024 and 1440 pixels. Verify there is no global horizontal overflow. Chart/table containers may scroll internally.
- Test slider recalculation, new seed, replay/pause/reset, touch and keyboard inspection, source links, CSV export, invalid input and request failures.
- Check WCAG A/AA rules, visible focus, baseline text contrast, console errors, failed requests and loading/empty states. Note the limits of automated checks.
- Check live route status, content type, security/cache headers, unknown routes, method errors, and API output equality with the local Python engine.
- Record the exact deployment URL, revision, CI/build status, screenshots, findings and remaining weaknesses in `docs/DEPLOYMENT_REPORT.md`.
- Do not mark the deployment verified until all relevant checks above pass against its real HTTPS URL.
