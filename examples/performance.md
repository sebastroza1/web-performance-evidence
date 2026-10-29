# Local p75 web performance comparison

**Source:** Owner-provided numbers, not independently validated.
**Scope:** Local test environment only; NOT production field data.
**Causality:** A before/after comparison alone does not prove which changes caused the differences.

| Metric | Before | After | Improvement | Status |
|---|---:|---:|---:|---|
| DOMContentLoaded | 3.77 s | 2.16 s | +42.7% | improved |
| Load | 4.27 s | 3.38 s | +20.8% | improved |
| FCP | 4.04 s | 2.41 s | +40.3% | improved |
| LCP | 4.04 s | 3.46 s | +14.4% | improved |
| CLS | 0.002  | 0.062  | -3000.0% | regressed |
| Initial transferred bundle | 773.83 kB | 507.85 kB | +34.4% | improved |

## Metric definitions

- **DOMContentLoaded:** Time until the HTML document is parsed and deferred scripts have executed.
- **Load:** Time until the page load event fires after dependent resources finish.
- **FCP:** First Contentful Paint: time until the first visible content is painted.
- **LCP:** Largest Contentful Paint: time until the largest visible content element is painted.
- **CLS:** Cumulative Layout Shift: visual stability score; lower is better.
- **Initial transferred bundle:** Bytes transferred for the measured initial application load.

## Interpreting Core Web Vitals

- FCP should be <= 1.8 seconds for a 'good' lab result; the measured 2.41 seconds remains above that threshold.
- LCP should be <= 2.5 seconds for 'good' performance; these local p75 results currently do not meet that threshold.
- CLS should be <= 0.1 for 'good' stability; the current 0.062 is within that threshold but represents a regression from 0.002.
- INP was not provided; do not claim that all Core Web Vitals pass.

## Reproducibility checklist

- [ ] Same browser version and device profile
- [ ] Same network throttling and caching strategy
- [ ] Same route and sample size, with run-count and variance documented
- [ ] Build revisions and optimization changes recorded
- [ ] Mobile and desktop checked separately
- [ ] No private user data or system identifiers exported
