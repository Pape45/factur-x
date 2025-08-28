# Factur‑X Express — Brand Pack (v0)

This folder contains a minimal, professional brand kit for **Factur‑X Express**.

## Files

- `fx-mark.svg` — monogram only (strokes inherit `currentColor`).
- `fx-mark-solid.svg` — monogram on rounded background, brand blue.
- `fx-wordmark-light.svg` — full logo for light backgrounds.
- `fx-wordmark-dark.svg` — full logo on dark background.
- `fx-favicon.svg` — square favicon (SVG).
- `colors.css` — CSS custom properties for easy theming.

## Quick usage (Next.js)

Place files under `/apps/web/public/brand/` and reference them:

```tsx
// apps/web/components/Logo.tsx
export function Logo({ variant = "mark", className = "" }: { variant?: "mark" | "solid" | "wordmark"; className?: string }) {
  const src =
    variant === "wordmark"
      ? "/brand/fx-wordmark-light.svg"
      : variant === "solid"
      ? "/brand/fx-mark-solid.svg"
      : "/brand/fx-mark.svg";
  return <img src={src} alt="Factur‑X Express" className={className} />;
}
```

For dark mode switch, load `fx-wordmark-dark.svg` and `fx-wordmark-light.svg` accordingly.

## Color tokens

```css
:root{
  --fx-accent: #2F6DF3;
  --fx-ink:    #0B0F19;
}
```

## Notes

- Wordmark uses **Inter** if available, otherwise falls back to system sans-serif.
- `fx-mark.svg` inherits `currentColor` => tint it via CSS (e.g., `.text-blue-600`).
- SVGs are tiny, crisp on all DPIs, and safe to inline.

## License

You (the project owner) have full rights to use, modify and distribute this logo within the Factur‑X Express project.