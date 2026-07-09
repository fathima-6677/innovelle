# 🛡️ AutiGuard Caregiver Console - React Client

[![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-blue?style=flat-square&logo=react)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat-square&logo=vite)](https://vite.dev/)

This directory houses the frontend web portal for the AutiGuard safety platform. It is built as a single-page application (SPA) with **React**, **TypeScript**, **Tailwind CSS**, and **Vite**.

## 🎨 Design System & UI Features

- **Glassmorphic Obsidian Aesthetics**: Rich dark mode dashboard built with high-contrast elements, neon accent borders, and subtle glowing overlays.
- **Vitals Telemetry Indicators**: Dynamic charts (heart rate, battery index, stress metrics) fed directly by a live WebSocket pipeline.
- **Interactive Geospatial Tracking**: Integrated Leaflet/Google Maps tracking wearer location lines and 100m geofence safe zones.
- **Liquid Glass Overlay Alerts**: 30% screen sheet notifications for falls, noise alerts, and geofence violations, including audio text-to-speech warnings.

## 🛠️ Getting Started

### Local Development
1. Install package dependencies:
   ```bash
   npm install
   ```
2. Launch the Vite dev server:
   ```bash
   npm run dev
   ```
   *The client will run on [http://localhost:5173/](http://localhost:5173/).*

### Production Build
Build optimized static production files inside the `dist/` directory:
```bash
# Set your API gateway address
$env:VITE_API_URL="https://YOUR_API_GATEWAY_SUBDOMAIN.execute-api.ap-south-1.amazonaws.com/prod/"
npm run build
```

---

*For full backend setup, AWS CDK deployment, and containerization instructions, refer to the [Root README](../README.md).*
