# Design System

## Overview

Wireframe low-fidelity untuk memvalidasi arsitektur informasi, urutan tugas, dan kelengkapan state CERNO sebelum desain visual final. Pengguna membukanya pada laptop atau ponsel di lingkungan sehari-hari, sering kali dalam keadaan ragu atau tertekan setelah menerima pesan mencurigakan; tampilan terang, tenang, dan sangat terstruktur membantu mereka memeriksa informasi tanpa distraksi.

## Visual Theme

- Monokrom dengan netral dingin dan satu aksen abu kebiruan yang sangat terbatas.
- Garis 1–2 px, sudut kecil, bayangan minimal, dan tekstur placeholder bergaris putus-putus.
- Tata letak editorial yang tegas seperti referensi worksheet, tetapi memakai affordance produk yang familiar.
- Tidak ada ilustrasi final, foto, gradient, glass effect, atau dekorasi yang dapat disalahartikan sebagai desain high-fidelity.

## Color Palette

- Canvas: `oklch(0.975 0.004 245)`
- Surface: `oklch(0.995 0.003 245)`
- Subtle surface: `oklch(0.945 0.006 245)`
- Border: `oklch(0.36 0.012 245)`
- Text: `oklch(0.24 0.012 245)`
- Muted text: `oklch(0.50 0.010 245)`
- Primary ink: `oklch(0.29 0.018 245)`
- Risk states use pattern, label, and icon in addition to restrained tonal differences.

## Typography

- Use the native system sans-serif stack for every product label and body copy.
- Use a system monospace stack for eyebrow labels, IDs, metadata, and wireframe annotations.
- Fixed scale: 12, 14, 16, 20, 28, 40 px.
- Keep prose within 70 characters per line where practical.

## Layout

- Public pages use a centered 1180 px frame with a simple top navigation.
- Authenticated and admin pages use a left sidebar plus content region.
- Primary analysis pages place input and guidance side by side on desktop, stacked on mobile.
- Dense lists become stacked records below tablet width.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 72 px.

## Components

- Buttons: rectangular, compact, consistent hierarchy for primary, secondary, and quiet actions.
- Inputs: visible label, hint or constraint, full border, and explicit error/help region.
- Tabs: text labels with border and selected background; never color-only.
- Panels: use only for bounded tasks, evidence groups, status, or records.
- Status labels: uppercase monospace prefix plus plain-language title.
- Empty/loading/error states: explain what happened and the next available action.
- Wireframe placeholder: dashed boundary with a short purpose label.

## Interaction

- Navigation and prototype transitions may work locally, but all data remains hardcoded.
- Forms never send data and file upload never reads or uploads a file.
- Mock actions show static or local-only state where useful for demonstrating flow.
- Focus states use a 2 px outline with offset. Hover never changes layout.
- Respect reduced-motion settings; transitions are limited to 150–200 ms state changes.
