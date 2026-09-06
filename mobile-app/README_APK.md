# EXPIRY.ALERT — Mobile APK (Offline + Phone notification bar)

This `mobile-app/` is the offline APK wrapper. No Django server needed — data stays on phone (`localStorage`), notifications fire on the **phone notification bar** even when app is closed.

## What it does
- **Store:** Medicine/Food name/qty/expiry in `localStorage` (offline)
- **Status:** Safe (>7d Green), Expiring Soon (≤7d Orange — tomorrow = 1d triggers), Expired (Red)
- **Phone bar:** Uses **Capacitor LocalNotifications** (native) + fallback **Web Notifications** (PWA). On every app open, checks expiry and schedules:
  - `Expired: Bread` → red, `Expiring soon: Paracetamol` (tomorrow) → orange
  - Shows in Android notification shade, tap opens app

## File map
- `capacitor.config.json` — appId `com.yash.expiryalert`
- `www/index.html` — UI
- `www/js/app.js` — localStorage + `daysUntil()` + `statusOf()` + `LocalNotifications.schedule()`
- `www/manifest.json` + `www/icons/*` — PWA

## Try PWA now (no build)
1. Django PWA already does same: `http://127.0.0.1:8000/dashboard/` → phone Chrome → `⋮ → Install app` → offline + notification bar via Web API (allow in footer).
2. Or open `mobile-app/www/index.html` directly in phone browser → Install → offline.

## Build real APK

### Prereq
- Node 18+, Java 17, Android Studio (SDK + Gradle)
```bash
brew install openjdk@17
brew install --cask android-studio
# set JAVA_HOME, ANDROID_SDK_ROOT
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
```

### Build
```bash
cd "yash prject/mobile-app"
npm install
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/local-notifications
npx cap add android
npx cap sync
npx cap open android   # opens Android Studio → Build → Build APK(s) → app-debug.apk
# or CLI:
cd android && ./gradlew assembleDebug
# APK at android/app/build/outputs/apk/debug/app-debug.apk
```

### Permissions (auto)
`LocalNotifications` adds `POST_NOTIFICATIONS` (Android 13+). On first launch, tap `Allow phone alerts` → system prompt → bar notifications enabled.

### Test tomorrow expiry
- Add Medicine `expiry = tomorrow` → immediately fires `Expiring soon: <name> (1d)` in notification bar.
- Kill app, reopen → again checks and fires for expired/expiring.

### Why not Formspree/SMTP?
APK is fully offline — no email, no server, no Formspree. Formspree endpoint `https://formspree.io/f/xeaqlvwp` remains for `www` contact form when online, but phone alerts are local.

