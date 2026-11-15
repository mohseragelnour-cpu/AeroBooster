// Prototype P1 predictions: 12 L salt in a 300 mm x 200 mm vessel (14 L gross)
const E = require("../simulator/src/engine.js");
const k = { rw100: [0.055, 0.10], rw150: [0.055, 0.15], rw200: [0.055, 0.20] };
const D = 0.30, Hv = 0.20, Vsalt = 12;
function G(kk, t) { const Ai = 2 * Math.PI * D * D / 4 + Math.PI * D * Hv, Do = D + 2 * t, Ho = Hv + 2 * t + 0.04, Ao = 2 * Math.PI * Do * Do / 4 + Math.PI * Do * Ho; return { G: 1.15 * kk * Math.sqrt(Ai * Ao) / t, Do, Ho }; }
const S = E.Store(Vsalt, 0);                      // enthalpy model of 12 L salt (mass = 12 x 1.9 x 0.9)
const steelKg = (2 * Math.PI * D * D / 4 + Math.PI * D * Hv) * 0.003 * 7900, cSteel = 0.5; // 3 mm wall, kJ/kgK
console.log("salt kg", S.m.toFixed(1), "steel kg", steelKg.toFixed(1), "usable 200-255 kWh", S.usable.toFixed(2));
const Hst = T => S.H_of(T) + steelKg * cSteel * (T - 25);
console.log("charge energy 25->255 kWh (salt+steel)", ((Hst(255) - Hst(25)) / 3600).toFixed(2));
for (const [n, [kk, t]] of Object.entries(k)) {
  const g = G(kk, t), Ta = 30;
  // cooldown from 255 with lid closed, 1-minute steps
  let T = 255, H = Hst(255), tm = 0; const marks = {};
  while (T > 120 && tm < 200 * 60) { H -= g.G * (T - Ta) * 60 / 1000; tm++; let lo = 25, hi = 300; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (Hst(m) < H) lo = m; else hi = m; } T = (lo + hi) / 2;
    for (const mk of [230, 220, 200, 150]) if (!marks[mk] && T <= mk) marks[mk] = (tm / 60).toFixed(1); }
  console.log(`${n}: G ${g.G.toFixed(3)} W/K, outer D ${(g.Do * 100).toFixed(0)} cm H ${(g.Ho * 100).toFixed(0)} cm, hold at 245 C needs ${(g.G * (245 - Ta)).toFixed(0)} W, cool 255->230 ${marks[230]} h, ->220 ${marks[220]} h, ->200 ${marks[200]} h, ->150 ${marks[150]} h`);
}
// plate test: 3 kg water from 30 C; plate D 0.30 m. What rise in 10 min at various fluxes?
const A = Math.PI * D * D / 4;
for (const q of [2, 3, 4, 5, 6]) { const P = q * A * 1000, dT = P * 600 / (3 * 4186); console.log(`flux ${q} kW/m2 -> ${P.toFixed(0)} W -> 3 kg water +${dT.toFixed(1)} K in 10 min`); }
console.log("plate area m2", A.toFixed(4), "home kisra flux needed 4.8 kW/m2 ->", (4.8 * A * 1000).toFixed(0), "W on this plate");
