# Web Performance Evidence Lab

A dependency-free Python laboratory for validating, comparing and visualizing owner-provided local p75 web performance measurements. It produces a reproducible Markdown report and accessible SVG chart while preserving the distinction between supplied data and independently reproduced evidence.

## Problem and approach

Before/after performance numbers are easy to overstate. This project treats provenance as part of the input contract, validates every value, calculates direction-aware percentage changes, flags regressions and explains relevant thresholds without claiming production telemetry or causality.

The supplied fixture records local p75 measurements associated with an AutismoConecta optimization case study. It contains no URL, user data, credentials or private infrastructure details.

## Architecture

`owner-provided JSON -> provenance validation -> comparison -> Markdown + SVG`

See [docs/architecture.md](docs/architecture.md) for the evidence boundary and the controlled future extension path.

## Technology

- Python 3.11+ standard library only.
- `unittest` for calculation, validation, provenance and visualization checks.
- SVG generated directly from validated data for a portable, accessible visual artifact.
- GitHub Actions on Python 3.11 and 3.12, including reproducibility checks for committed outputs.

## Run locally

```bash
python -m unittest discover -s tests -v
python -m perf.cli \
  --input fixtures/autismoconecta_local_p75.json \
  --output examples/performance.md \
  --chart examples/performance.svg
```

The generated artifacts are versioned at [examples/performance.md](examples/performance.md) and [examples/performance.svg](examples/performance.svg).

## Verified example results

| Metric | Before | After | Improvement | Interpretation |
|---|---:|---:|---:|---|
| DOMContentLoaded | 3.77 s | 2.16 s | +42.7% | improved locally |
| Load | 4.27 s | 3.38 s | +20.8% | improved locally |
| FCP | 4.04 s | 2.41 s | +40.3% | improved, still above 1.8 s lab threshold |
| LCP | 4.04 s | 3.46 s | +14.4% | improved, still above 2.5 s lab threshold |
| CLS | 0.002 | 0.062 | -3000.0% | regression, though still below 0.1 |
| Initial transferred bundle | 773.83 kB | 507.85 kB | +34.4% | reduced locally |

These are **owner-provided local p75 values**, not independently verified telemetry or real-user field data. Measurement conditions such as browser version, device, route, cache, throttling, run count and variance were not supplied, so no specific code change is claimed as the cause.

## Verification

```bash
python -m compileall -q perf tests
python -m unittest discover -s tests -v
python -m perf.cli --input fixtures/autismoconecta_local_p75.json --output examples/performance.md --chart examples/performance.svg
git diff --exit-code -- examples
```

## Limitations

- The dataset is supplied by the project owner and has not been independently reproduced.
- Results describe a local test context, not production users.
- INP was not provided, so the project cannot claim that all Core Web Vitals pass.
- The current fixture assumes lower values are better; the engine supports explicit `higher_is_better` metrics for controlled extensions.
- No load test or automated request is sent to AutismoConecta.

## Next steps

1. Record browser, device, route, cache, throttling, sample count and variance alongside future measurements.
2. Add Playwright and Lighthouse only against a separately owned or explicitly authorized demo application.
3. Compare repeated runs statistically before making causal claims.
