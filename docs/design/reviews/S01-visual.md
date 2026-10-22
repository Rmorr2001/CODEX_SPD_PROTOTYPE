# S01 visual comparison

**Screen:** Home, `/app/`. **Spec:** [S01](../screen-specs.md#s01-home).
**Concept:** [public board](../references/public-pages.png), left HOME panel.
**Evidence:** [desktop](../evidence/S01-desktop.png),
[mobile](../evidence/S01-mobile.png), rendered from the local seeded Django
fixture at `http://127.0.0.1:8871`; not the live Railway deployment.

## Final verdict: YEAH / PASS

Reopened the refreshed desktop/mobile screenshots after the builder rebuilt the
same local seeded fixture. SVG arrows now render clearly in navigation and CTAs;
the hero eyebrow is white and readable. Both required findings below are closed.
The responsive hierarchy, spacing, legibility and red/black identity pass.

## Initial comparison and correction history

Opened the concept and both actual screenshots. The implementation captures the
black header, white wordmark, large editorial hero, strong red primary action,
outlined secondary action and clean white purpose section. The numbered pillars
and restrained recruitment section are coherent adaptations. The repository's
chapter photograph replaces invented generated people; omitting fabricated
upcoming events is correct. At 390px the content stacks cleanly, readable CTAs
remain visible and the screenshot shows no horizontal overflow.

Two required rendering fixes:

1. Missing-glyph squares appear in the member-login link, Join button,
   recruitment button and Instagram link. Replace font-dependent arrow glyphs
   with an inline SVG or another reliably rendered icon.
2. The small red hero eyebrow is difficult to read over the dark photograph.
   Use a high-contrast light label and keep the brand red in actions/rules.

During initial review, source already contained an `Arrow` SVG and a white hero
eyebrow, but screenshots showed the earlier rendering. The builder rebuilt and
recaptured both screenshots; the final review above verifies the actual result.
No other blocking visual changes requested.

Optional future polish: compact the wrapping mobile header; its current
three-row arrangement is usable and does not block this page.
