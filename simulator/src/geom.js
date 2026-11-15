/* AeroBooster C.3 – store geometry, insulation and heat-loss coefficient.
   Module: vertical cylinder, saj plate on top (D >= 0.40 m). Central: rectangular box, H = 0.5 m, saj plates and oven on the lid.
   G (W/K) = 1.15 x k x sqrt(A_inner x A_outer) / t  (mean-area wall, +15 % for plate rim, supports, heater and oil penetrations). */
(function (root) {
  "use strict";
  const INSUL = {
    rw100: { ar: "صوف صخري 100 مم", k: 0.055, t: 0.10, rho: 120, usdM3: 180 },
    rw150: { ar: "صوف صخري 150 مم", k: 0.055, t: 0.15, rho: 120, usdM3: 180 },
    rw200: { ar: "صوف صخري 200 مم", k: 0.055, t: 0.20, rho: 120, usdM3: 180 },
    rw250: { ar: "صوف صخري 250 مم", k: 0.055, t: 0.25, rho: 120, usdM3: 180 },
    hyb:   { ar: "50 مم ميكروبوري + 100 مم صوف صخري", k: 0.15 / (0.05 / 0.024 + 0.10 / 0.055), t: 0.15, rho: 160, usdM3: 4000 },
    mp100: { ar: "ميكروبوري 100 مم (افتراض النسخة C)", k: 0.024, t: 0.10, rho: 250, usdM3: 12000 }
  };
  const FILL = 0.9, RHO_SALT = 1.90;
  function geom(storeL, central, insulKey) {
    const ins = INSUL[insulKey] || INSUL.rw150, t = ins.t, V = storeL / 1000 / FILL;
    let g;
    if (!central) {
      const D = Math.max(0.40, Math.cbrt(4 * V / Math.PI)), H = V / (Math.PI * D * D / 4);
      const Ai = 2 * Math.PI * D * D / 4 + Math.PI * D * H, Do = D + 2 * t, Ho = H + 2 * t + 0.05;
      const Ao = 2 * Math.PI * Do * Do / 4 + Math.PI * Do * Ho;
      g = { shape: "cyl", D, H, Do, Ho, Ai, Ao, top: Math.PI * D * D / 4, shell: Ai * 0.002 * 7900, insVol: Math.PI * (Do * Do - D * D) / 4 * H + 2 * Math.PI * Do * Do / 4 * t };
    } else {
      const H = 0.5, A = V / H, L = Math.sqrt(A * 1.5), W = A / L;
      const Ai = 2 * A + 2 * H * (L + W), Lo = L + 2 * t, Wo = W + 2 * t, Ho = H + 2 * t + 0.08;
      const Ao = 2 * Lo * Wo + 2 * Ho * (Lo + Wo);
      g = { shape: "box", L, W, H, Lo, Wo, Ho, Ai, Ao, top: A, shell: Ai * 0.004 * 7900, insVol: Lo * Wo * Ho - L * W * H };
    }
    g.G = 1.15 * ins.k * Math.sqrt(g.Ai * g.Ao) / t;
    g.salt = storeL * RHO_SALT * FILL;
    g.insKg = g.insVol * ins.rho; g.insUsd = g.insVol * ins.usdM3;
    g.weight = g.salt + g.shell + g.insKg + (central ? 60 : 8);
    g.ins = ins; g.insulKey = insulKey;
    return g;
  }
  const API = { geom, INSUL };
  if (typeof module !== "undefined" && module.exports) module.exports = API; else root.ABGeom = API;
})(typeof window !== "undefined" ? window : globalThis);
