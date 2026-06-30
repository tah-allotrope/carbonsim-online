/**
 * CarbonSim Online — VND / tonnes formatters (plan 2026-06-30 PHASE-02).
 *
 * All formatting is display-only; engine/DB/JSON stay numeric floats. The
 * underlying values are exact in đ and tCO2e; we just dress them for human
 * reading.
 *
 * Two policies:
 *
 *   formatVnd / formatTonnes — full Vietnamese dot-grouped form. Used for
 *     headline tiles ("136.000 đ/tCO2e", "511.473.846 tCO2e") and stat cards.
 *
 *   formatVndAbbrev / formatTonnesAbbrev — abbreviated with T/B/M/K suffix.
 *     Used for inline deltas (CityRenderer floaters, log lines, compact table
 *     cells) where the full form would blow out the layout.
 *
 * Vietnamese locale (`vi-VN`) uses `.` for thousands and `,` for decimals.
 * Integers print as "1.234.567" — no decimal point.
 */

const _vndFullFmt = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 });
const _tonneFullFmt = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 });

function formatVnd(n) {
  if (n == null || isNaN(n)) return "—";
  return _vndFullFmt.format(Math.round(n)) + " đ";
}

function formatVndAbbrev(n) {
  if (n == null || isNaN(n)) return "—";
  const abs = Math.abs(n);
  const sign = n < 0 ? "-" : "";
  if (abs >= 1e12) return sign + (abs / 1e12).toFixed(1) + "T đ";
  if (abs >= 1e9) return sign + (abs / 1e9).toFixed(1) + "B đ";
  if (abs >= 1e6) return sign + (abs / 1e6).toFixed(1) + "M đ";
  if (abs >= 1e3) return sign + (abs / 1e3).toFixed(1) + "K đ";
  return sign + abs.toFixed(0) + " đ";
}

function formatTonnes(n) {
  if (n == null || isNaN(n)) return "—";
  return _tonneFullFmt.format(Math.round(n)) + " t";
}

function formatTonnesAbbrev(n) {
  if (n == null || isNaN(n)) return "—";
  const abs = Math.abs(n);
  const sign = n < 0 ? "-" : "";
  if (abs >= 1e9) return sign + (abs / 1e9).toFixed(1) + "B t";
  if (abs >= 1e6) return sign + (abs / 1e6).toFixed(1) + "M t";
  if (abs >= 1e3) return sign + (abs / 1e3).toFixed(1) + "K t";
  return sign + abs.toFixed(0) + " t";
}

window.formatVnd = formatVnd;
window.formatVndAbbrev = formatVndAbbrev;
window.formatTonnes = formatTonnes;
window.formatTonnesAbbrev = formatTonnesAbbrev;
