# DevAgent.Dev Branding Assets

This directory contains the **DevAgent.Dev** corporate-identity assets used by this
deployment: favicons, logos, splash images, app icons, and web-app-manifest icons.

## Source of truth

- Identity guidelines: `~/DevAgent.Dev/branding/DevAgent.Dev-Branding-CI.md` (v1.0, July 2026)
- Master artwork: `~/DevAgent.Dev/brand-assets/logo-sizes/`
- Web design system: `~/DevAgent.Dev/website/DESIGN_SYSTEM.md`

Assets here are generated from the master symbol (`devagent-icon-master.png`) by
`scripts/brand/gen_brand_assets.py`. Only the symbol-only configuration is used, per
CI §5.1 (favicons, app icons, small spaces). Proportions, colours and node count are
never altered (§5.5); the white background is cut and a white plate is added where the
guidelines require a light background under the mark (§5.4, dark splash and maskable
PWA icons).

| File | Purpose |
|---|---|
| `favicon.png`, `favicon-96x96.png`, `favicon.ico`, `favicon.svg` | Browser tab / sidebar mark (symbol on white) |
| `apple-touch-icon.png` | iOS home-screen icon |
| `logo.png`, `web-app-manifest-*.png` | PWA icons, `maskable` safe-zone padding |
| `splash.png` | Light splash (transparent mark) |
| `splash-dark.png` | Dark splash (mark on white rounded plate) |
| `brand/devagent-mark.png` | Transparent master mark, 512 px |
| `brand/devagent-horizontal.png` | Primary horizontal lockup with bilingual slogan (min 800 px wide, CI §5.3) |

Brand colours: Deep Ocean Blue `#004488`, Silver Connectivity `#C0C0C0`,
Growth Green `#00CC66`, Slate Charcoal `#333333`. Type: Inter (Latin), Noto Sans Thai (Thai).

## Licence notice

This deployment replaces Open WebUI branding. The Open WebUI `LICENSE` permits that
only when one of the following holds: (i) at most fifty (50) users in any rolling
thirty-day period, (ii) prior written permission from the copyright holder, or
(iii) an executed enterprise licence. The operator is responsible for staying within
one of those conditions. The "About" settings panel keeps the upstream Open WebUI
attribution, and the original assets remain available in upstream git history.
