# Lunisolar OS

**Lunisolar OS** is a cycle-based personal operating system integrating lunar phases and solar seasons—combining ancient timekeeping with modern productivity frameworks for intentional living, reflection, execution, and growth.

This repo generates iPhone-friendly `.ics` calendars that include:
- lunar phase **windows** (multi-day bars with guidance)
- key phase **marker days** (New Moon / First Quarter / Full / Third Quarter)
- **equinoxes & solstices**
- optional Wheel-of-the-Year cross-quarter markers

> Note: lunar phase times are approximated (good for day-level planning). For astronomy-grade timing, swap the phase engine for Skyfield.

---

## Quick start

### 1) Generate a calendar
```bash
python3 src/generate_lunisolar_os.py --year 2026 --out calendar/lunisolar_os_2026.ics
```

### 2) Host it (so iPhone can subscribe)
Upload the `.ics` to GitHub and use the **raw** link.

Example raw link:
```
https://raw.githubusercontent.com/<USER>/<REPO>/main/calendar/lunisolar_os_2026.ics
```

On iPhone, subscribe via:
- Settings → Calendar → Accounts → Add Account → Other → **Add Subscribed Calendar**
- paste the link, but replace `https://` with `webcal://` for best compatibility

Example:
```
webcal://raw.githubusercontent.com/<USER>/<REPO>/main/calendar/lunisolar_os_2026.ics
```

---

## Suggested use (Ryan-mode)

- **New Moon → First Quarter:** Build (plan + set intentions + define risk)
- **First Quarter → Full Moon:** Execute (A+ setups only; process > outcome)
- **Full Moon → Third Quarter:** Review (journal insights; extract 1 tweak)
- **Third Quarter → New Moon:** Refine (prune habits; restore sleep; simplify)

---

## File structure
- `src/generate_lunisolar_os.py` — calendar generator
- `calendar/` — generated `.ics` feeds

---

## License
MIT
