/* AeroBooster revision C – simulation engine (browser and Node).
   Port of aerobooster_revC_model.py, generalised to scenarios of any scale.
   365 days, 15-minute steps. Loads are served only above their temperature floor; no clamps;
   the salt-store energy balance is returned with every run. Calculated, not measured. */
(function (root) {
  "use strict";
  const CPW = 4.186, DT = 0.25, STEPS = 96;

  // ---------------------------------------------------------------- random (seeded)
  function rng(seed) {
    let s = (seed >>> 0) || 1;
    return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  }

  // ---------------------------------------------------------------- built-in synthetic climates
  // Day-type probabilities per month: clear, hazy, partly (broken cloud), heavy (dust/overcast)
  const P_SAHEL = [[.75,.20,0,.05],[.75,.20,0,.05],[.70,.25,0,.05],[.55,.35,0,.10],[.50,.38,.02,.10],[.45,.35,.10,.10],
                   [.35,.15,.40,.10],[.30,.15,.45,.10],[.40,.15,.35,.10],[.70,.22,.03,.05],[.75,.20,0,.05],[.75,.20,0,.05]];
  const PROFILES = {
    sahel_dry: { label: "Dry Sahel (Khartoum type)", lat: 15.6, P: P_SAHEL,
      T: [23,25,28,32,34,34,32,31,32,32,28,24], swing: 7 },
    sahel_rain: { label: "Sahel with a long rainy season (El Obeid / Nyala type)", lat: 13.2,
      P: [[.75,.20,0,.05],[.75,.20,0,.05],[.70,.25,0,.05],[.60,.30,0,.10],[.45,.30,.15,.10],[.30,.20,.40,.10],
          [.20,.10,.55,.15],[.20,.10,.55,.15],[.30,.10,.45,.15],[.60,.20,.15,.05],[.75,.20,0,.05],[.75,.20,0,.05]],
      T: [21,24,27,30,31,30,27,26,27,28,25,22], swing: 7 },
    coastal: { label: "Hot humid coast (Port Sudan type)", lat: 19.6,
      P: [[.55,.25,.15,.05],[.60,.25,.10,.05],[.65,.25,.05,.05],[.65,.30,0,.05],[.55,.40,0,.05],[.45,.45,0,.10],
          [.40,.45,0,.15],[.40,.45,0,.15],[.50,.40,0,.10],[.60,.30,.05,.05],[.55,.25,.15,.05],[.55,.25,.15,.05]],
      T: [24,24,25,28,31,33,35,35,33,30,28,25], swing: 5 },
    temperate40: { label: "Temperate, about 40° N (Absheron / Sumqayit type)", lat: 40.6,
      P: [[.25,.15,.30,.30],[.30,.15,.30,.25],[.35,.15,.30,.20],[.45,.15,.25,.15],[.60,.15,.15,.10],[.70,.15,.10,.05],
          [.75,.15,.05,.05],[.75,.15,.05,.05],[.65,.15,.15,.05],[.50,.15,.20,.15],[.35,.15,.25,.25],[.25,.15,.30,.30]],
      T: [4,4,7,12,18,23,26,26,21,16,10,6], swing: 5 }
  };
  const DAY_F = { clear: [1, 1], hazy: [0.55, 0.85], partly: [null, 0.75], heavy: [0.15, 0.45] };
  const TYPES = ["clear", "hazy", "partly", "heavy"];
  const monthOf = d => Math.min(11, Math.floor(d / 30.42));

  // ---------------------------------------------------------------- sun
  function sunPos(lat, day, t) {
    const dec = 0.40928 * Math.sin(2 * Math.PI * (284 + day + 1) / 365);
    const w = (15 * (t - 12)) * Math.PI / 180, la = lat * Math.PI / 180;
    const s = Math.sin(la) * Math.sin(dec) + Math.cos(la) * Math.cos(dec) * Math.cos(w);
    return { s, dec, w };
  }
  function clearSky(lat, day, t) {
    const { s, dec, w } = sunPos(lat, day, t);
    if (s <= 0.02) return { dni: 0, ghi: 0, s, dec, w };
    const altDeg = Math.asin(s) * 180 / Math.PI;
    const am = 1 / (s + 0.50572 * Math.pow(6.07995 + altDeg, -1.6364));
    const dni = 1353 * Math.pow(0.7, Math.pow(am, 0.678)) * 0.88;
    const ghi = 1098 * s * Math.exp(-0.057 / s) * 0.97;
    return { dni, ghi, s, dec, w };
  }

  // ---------------------------------------------------------------- climate (synthetic, or calibrated to NASA POWER)
  // power: {ghi:[12], dni:[12], t:[12], tmax:[12], tmin:[12]}  (kWh/m2/day, C) – optional
  function makeClimate(opts) {
    const lat = opts.lat, prof = PROFILES[opts.profile || "sahel_dry"], R = rng(opts.seed || 7);
    const power = opts.power || null;
    const dayType = new Array(365);
    let P = prof.P;
    if (power) {             // derive day-type mix from the ratio of POWER GHI to the clear-sky model
      P = [];
      for (let m = 0; m < 12; m++) {
        let cg = 0, n = 0;
        for (let d = 0; d < 365; d++) if (monthOf(d) === m) { for (let k = 0; k < STEPS; k++) cg += clearSky(lat, d, k * DT).ghi * DT / 1000; n++; }
        const kk = power.ghi[m] / (cg / n);
        const pc = Math.max(0, Math.min(1, (kk - 0.68) / 0.32));
        const r = 1 - pc;
        P.push([pc, r * 0.5, r * 0.3, r * 0.2]);
      }
    }
    for (let d = 0; d < 365; d++) {
      if (opts.storm && d >= 14 && d <= 16) { dayType[d] = "heavy"; continue; }
      const p = P[monthOf(d)], r = R(); let c = 0, ty = "clear";
      for (let i = 0; i < 4; i++) { c += p[i]; if (r <= c) { ty = TYPES[i]; break; } }
      dayType[d] = ty;
    }
    // per-month calibration factors so that monthly means match POWER (1.0 for synthetic profiles)
    const fG = new Array(12).fill(1), fD = new Array(12).fill(1);
    const R2 = rng((opts.seed || 7) + 99);
    const onoff = [];  // beam on/off pattern for partly-cloudy hours
    for (let d = 0; d < 365; d++) { const row = []; for (let k = 0; k < STEPS; k += 4) row.push(R2() < 0.5); onoff.push(row); }
    function raw(d, k) {
      const t = k * DT, cs = clearSky(lat, d, t), ty = dayType[d], f = DAY_F[ty];
      let dni = cs.dni, ghi = cs.ghi;
      if (ty === "partly") { const on = onoff[d][k >> 2]; dni = on ? dni : 0; ghi = ghi * (on ? 1 : 0.5); }
      else { dni *= f[0]; ghi *= f[1]; }
      return { dni, ghi, cs };
    }
    if (power) {
      const sg = new Array(12).fill(0), sd = new Array(12).fill(0), nn = new Array(12).fill(0);
      for (let d = 0; d < 365; d++) { const m = monthOf(d); nn[m]++; for (let k = 0; k < STEPS; k++) { const x = raw(d, k); sg[m] += x.ghi * DT / 1000; sd[m] += x.dni * DT / 1000; } }
      for (let m = 0; m < 12; m++) {
        fG[m] = Math.min(1.25, power.ghi[m] / (sg[m] / nn[m]));
        if (power.dni && power.dni[m] > 0) fD[m] = Math.min(1.25, power.dni[m] / (sd[m] / nn[m]));
      }
    }
    const Tm = power ? power.t : prof.T;
    const sw = power && power.tmax ? power.tmax.map((x, i) => Math.max(2, (x - power.tmin[i]) / 2)) : new Array(12).fill(prof.swing);
    const latAbs = Math.abs(lat);
    function at(d, k) {
      const m = monthOf(d), x = raw(d, k), t = k * DT;
      const dni = x.dni * fD[m], ghi = x.ghi * fG[m], s = x.cs.s;
      if (s <= 0.02) return { troughDni: 0, gt: 0, ghi: 0, dniN: 0, ta: Tm[m] + sw[m] * Math.sin(2 * Math.PI * (t - 9) / 24) };
      const dhi = Math.max(0, ghi - dni * s);
      const decE = lat >= 0 ? x.cs.dec : -x.cs.dec;          // panel faces the equator, tilt = |lat|
      const cosT = Math.max(0, Math.cos(decE) * Math.cos(x.cs.w));
      const gt = dni * cosT + dhi * (1 + Math.cos(latAbs * Math.PI / 180)) / 2;
      const troughDni = s > Math.sin(15 * Math.PI / 180) ? dni * Math.cos(x.cs.dec) : 0;
      return { troughDni, gt, ghi, dniN: dni, ta: Tm[m] + sw[m] * Math.sin(2 * Math.PI * (t - 9) / 24) };
    }
    return { at, dayType, lat, label: power ? "NASA POWER climatology" : prof.label };
  }

  // ---------------------------------------------------------------- salt store (enthalpy, kJ rel. 25 C)
  function Store(litres, egFrac) {
    const m = litres * 1.90 * 0.90, mSalt = m * (1 - (egFrac || 0)), st = 0.20 * m / 0.9 * 0.5;
    const cps = 1.40, cpl = 1.50, L = 97, T1 = 220, T2 = 230;
    const a = m * cps + st, b = m * (cps + cpl) / 2 + st, c = m * cpl + st;
    const H1 = a * (T1 - 25), H2 = H1 + mSalt * L + b * (T2 - T1);
    function H_of(T) {
      if (T <= T1) return a * (T - 25);
      if (T <= T2) { const f = (T - T1) / (T2 - T1); return H1 + f * mSalt * L + b * (T - T1); }
      return H2 + c * (T - T2);
    }
    function T_of(H) {
      if (H <= H1) return 25 + H / a;
      if (H >= H2) return T2 + (H - H2) / c;
      let lo = T1, hi = T2;
      for (let i = 0; i < 30; i++) { const mid = (lo + hi) / 2; if (H_of(mid) < H) lo = mid; else hi = mid; }
      return (lo + hi) / 2;
    }
    return { m, H_of, T_of, usable: (H_of(255) - H_of(200)) / 3600 };
  }

  // ---------------------------------------------------------------- run one module
  // sc: scenario (whole-site loads); cfg: per-module hardware and control; N modules share the loads.
  const RECEIVERS = { expected: [0.58, 5.61, 0.0136, 12], cautious: [0.55, 6.6, 0.016, 12] };

  function run(sc, cfg, climate) {
    const N = Math.max(1, cfg.modules | 0);
    const S = Store(cfg.storeL, cfg.egFrac);
    // central-plant options; defaults reproduce the 45 L module exactly
    const cascKw = cfg.cascKw || 1.0, cartsPerDay = cfg.cartsPerDay == null ? 2 : cfg.cartsPerDay;
    const stations = cfg.stations || 1, lidG = cfg.lidG == null ? 0.6 : cfg.lidG;
    const maxOut = cfg.maxOutKw || Infinity, loopDT = cfg.loopDT || 0, loopLossKw = cfg.loopLossKw || 0;
    let H = S.H_of(230), Tw = 45, soc = 0.8;
    const H0 = H;
    const rec = RECEIVERS[cfg.receiver || "expected"];
    const acc = { loop: 0, pv: 0, trough: 0, away: 0, loss: 0, jacket: 0, cascade: 0, cook: 0, flat: 0, divert: 0,
                  water: 0, tankloss: 0, cart: 0, bonus: 0, pvSpill: 0 };
    const stat = {};            // name -> [served, wanted]
    const weeks = {};           // flex name -> array of weekly counts
    const flexCount = {};
    let cartN = 0, bonusN = 0, minT = 999, minSoc = 1;
    let soilTr = 1, soilPv = 1;
    const daily = [];
    const sObj = (n) => (stat[n] || (stat[n] = [0, 0]));
    (sc.flex || []).forEach(f => { weeks[f.name] = []; flexCount[f.name] = 0; });
    const anyBake = (sc.flex || []).some(f => f.floor >= 215);
    for (let d = 0; d < 365; d++) {
      const dty = climate.dayType[d];
      if (d % 7 === 0) {
        if (d > 0) for (const f of (sc.flex || [])) weeks[f.name].push(flexCount[f.name]);
        for (const f of (sc.flex || [])) flexCount[f.name] = 0;
      }
      if (d % (cfg.cleanDays || 7) === 0) { soilTr = 1; soilPv = 1; }
      if (dty === "heavy") { soilTr -= 0.05; soilPv -= 0.03; }
      soilTr = Math.max(0.6, soilTr - (cfg.soilRate || 0.012) / 4 * 0); soilPv = Math.max(0.7, soilPv);
      const m = monthOf(d);
      const winter = sc.heating && sc.heating.months.indexOf(m) >= 0;
      const ev = {};
      const doneToday = {};
      let cartToday = 0, bonusToday = false;
      const daysLeft = 7 - d % 7;
      for (let k = 0; k < STEPS; k++) {
        const t = k * DT;
        const T = S.T_of(H);
        if (T < minT) minT = T;
        const w = climate.at(d, k), Ta = w.ta;
        // daily soiling
        const sTr = soilTr * (1 - 0.012 * (d % (cfg.cleanDays || 7))), sPv = soilPv * (1 - 0.006 * (d % (cfg.cleanDays || 7)));
        // ---- heat in
        let qTr = 0;
        if (cfg.troughM2 > 0 && w.troughDni > 0) {
          const dT = T + 35 - Ta;
          const q = cfg.troughM2 * (w.troughDni * rec[0] * sTr - (rec[1] * dT + rec[2] * dT * dT) / rec[3]) * 0.95 / 1000;
          if (q > 0 && soc > 0.12) { if (T < cfg.Tmax) qTr = q; else acc.away += q * DT; }
        }
        const qPvAll = cfg.pvM2 > 0 ? Math.min(cfg.pvM2 * 0.21, cfg.pvM2 * w.gt * 0.172 * sPv / 1000) : 0;
        const qPv = T < cfg.Tmax ? qPvAll : 0;
        acc.pvSpill += (qPvAll - qPv) * DT;
        // ---- schedule
        const start = (key, o) => {
          if (ev[key] && ev[key].active) return;
          ev[key] = { key, name: o.name, kwh: o.kwh, kw: o.kw, floor: o.floor, left: o.kwh, active: true, kind: o.kind, tankL: o.tankL || 0 };
          if (o.kind !== "cart" && o.kind !== "bonus") sObj(o.name)[1] += 1;
        };
        for (const f of (sc.fixed || [])) {
          if (Math.abs(t - f.t) < 1e-6 && (!f.weekdays || f.weekdays.indexOf(d % 7) >= 0)) {
            let kwh = f.kwh / N, kw = f.kw / N, tankL = 0;
            if (f.boilL) { tankL = f.boilL / N; kwh = tankL * CPW * (100 - Math.min(Tw, 95)) / 3600; kw = Math.max(kwh / 0.25, 0.05); }
            start(f.name + "@" + f.t, { name: f.name, kwh, kw, floor: f.floor, kind: "fixed", tankL });
          }
        }
        for (const f of (sc.flex || [])) {
          const need = f.perWeek - flexCount[f.name];
          if (doneToday[f.name] || need <= 0 || t < f.window[0] || t > f.window[1] || ev[f.name]) continue;
          if ((sc.flex || []).some(g => g !== f && ev[g.name] && ev[g.name].active && g.exclusive && f.exclusive)) continue;
          const urgent = need >= daysLeft;
          const late = t >= f.window[1] - 1 && need >= daysLeft - 1;
          if (T >= f.start || ((urgent || late) && T >= f.urgent)) {
            start(f.name, { name: f.name, kwh: f.kwh / N, kw: f.kw / N, floor: f.floor, kind: "flex" });
            doneToday[f.name] = true;
          }
        }
        const surplus = T >= cfg.Tmax - 3 && (qTr + qPvAll) > 0.2;
        if (cfg.surplus && surplus) {
          if (cartToday < cartsPerDay && !(ev.cart && ev.cart.active)) { start("cart", { name: "cart", kwh: 0.25, kw: 0.5, floor: 225, kind: "cart" }); cartToday++; }
          if (anyBake && !bonusToday && t >= 12 && t <= 16 && Object.keys(doneToday).length && !Object.values(ev).some(e => e.active && e.kind === "flex")) {
            start("bonus", { name: "bonus", kwh: 0.73, kw: 0.6, floor: 215, kind: "bonus" }); bonusToday = true;
          }
        }
        // ---- serve
        let qOut = 0, lidOff = false, tankDraw = 0, nActive = 0;
        // central plant: heat leaves through a thermal-oil loop of limited rating, and the plate needs loopDT more
        let want = 0;
        const dTof = (e) => (cfg.bakeDirect && e.floor >= 200) ? 0 : loopDT;   // bake stations sit on the store itself
        for (const key in ev) { const e = ev[key]; if (e.active && T >= e.floor + dTof(e)) want += e.kw; }
        const share = want > maxOut ? maxOut / want : 1;
        for (const key in ev) {
          const e = ev[key]; if (!e.active) continue;
          if (T >= e.floor + dTof(e)) {
            const take = Math.min(e.kw * share * DT, e.left);
            e.left -= take; qOut += take / DT; lidOff = true; nActive++;
            if (e.tankL && e.left <= 1e-9) tankDraw += e.tankL * CPW * (Tw - 25) / 3600 / DT;
            if (e.left <= 1e-9) {
              e.active = false;
              if (e.kind === "cart") { cartN++; acc.cart += e.kwh; }
              else if (e.kind === "bonus") { bonusN++; acc.bonus += e.kwh; }
              else { sObj(e.name)[0] += 1; acc.cook += e.kwh; if (e.kind === "flex") flexCount[e.name] += 1; }
            }
          } else {
            e.active = false;
            const served = e.kwh - e.left;
            if (e.kind === "cart") acc.cart += served; else if (e.kind === "bonus") acc.bonus += served; else acc.cook += served;
          }
        }
        // ---- losses, jacket, cascade
        const G = cfg.Gstore + lidG * Math.min(nActive, stations);
        const qLoop = nActive > 0 ? loopLossKw : 0;
        const loss = G * (T - Ta) / 1000;
        const jk = Tw < cfg.tankMax ? cfg.jacket * cfg.Gstore * (T - Ta) / 1000 : 0;
        const nearFull = T > cfg.thrHi, tail = T < cfg.thrLo && t >= 8 && t < 20;
        let casc = 0;
        if ((nearFull || tail) && T > Tw + 15 && Tw < cfg.tankMax) casc = Math.min(cascKw, (cfg.tankMax - Tw) * cfg.tankL * CPW / 3600 / DT);
        // ---- water side
        const dTw = Tw + 6 - Ta;
        let qFlat = 0;
        if (w.gt > 50) { const eta = 0.70 - (1.25 * dTw + 0.0048 * dTw * dTw) / w.gt; qFlat = Math.max(0, cfg.flatM2 * w.gt * eta / 1000); }
        const toTank = Tw < cfg.tankMax ? qFlat : 0, divert = qFlat - toTank;
        let draw = tankDraw;
        for (const wd of (sc.water || [])) {
          if (Math.abs(t - wd.t) < 1e-6) {
            const L = wd.litres / N;
            sObj(wd.name)[1] += 1;
            if (Tw >= wd.temp) { draw += L * CPW * (wd.temp - 25) / 3600 / DT; sObj(wd.name)[0] += 1; }
          }
        }
        if (winter) {
          const h = sc.heating, on = h.from > h.to ? (t >= h.from || t < h.to) : (t >= h.from && t < h.to);
          if (on) { sObj("heating")[1] += 1; if (Tw >= 40) { draw += h.kw / N; sObj("heating")[0] += 1; } }
        }
        const tankLoss = 0.8 * Math.pow(cfg.tankL / 120, 0.67) * (Tw - Ta) / 1000;
        // ---- update
        H += (qTr + qPv - qOut - loss - casc - qLoop) * DT * 3600; acc.loop += qLoop * DT;
        Tw += (toTank + jk + casc * 0.9 - draw - tankLoss) * DT * 3600 / (cfg.tankL * CPW);
        acc.trough += qTr * DT; acc.pv += qPv * DT; acc.loss += loss * DT; acc.jacket += jk * DT; acc.cascade += casc * DT;
        acc.flat += toTank * DT; acc.divert += divert * DT; acc.water += draw * DT; acc.tankloss += tankLoss * DT;
        // ---- controller electricity
        const pGen = cfg.ctrlPvW * w.gt / 1000 * 0.85 * sPv + (qPvAll - qPv) * 1000 * 0.3 / N;
        const pLoad = 3 + (qTr > 0 ? 10 : 0) + (cfg.troughM2 > 0 && w.troughDni > 0 ? 1 : 0) + (t >= 18 && t < 22 ? 12 : 0) + (t >= 19 && t < 21 && soc > 0.3 ? 10 : 0);
        soc = Math.min(1, Math.max(0.05, soc + (pGen - pLoad) * DT / 1200));
        if (soc < minSoc) minSoc = soc;
      }
      daily.push({ T: S.T_of(H), Tw, dty });
    }
    for (const f of (sc.flex || [])) weeks[f.name].push(flexCount[f.name]);
    const balance = (H - H0) / 3600 - (acc.trough + acc.pv - acc.loss - acc.cascade - acc.cook - acc.cart - acc.bonus - acc.loop);
    return { N, stat, weeks, acc, cartN, bonusN, minT, minSoc, daily, balance, usable: S.usable, saltKg: S.m, sc, cfg };
  }

  function summarize(r) {
    const out = { loads: [], flex: [], water: [], N: r.N };
    const sc = r.sc;
    const fixedNames = [...new Set((sc.fixed || []).map(f => f.name))];
    for (const n of fixedNames) { const s = r.stat[n] || [0, 0]; out.loads.push({ name: n, pct: s[1] ? 100 * s[0] / s[1] : NaN }); }
    for (const f of (sc.flex || [])) {
      const w = r.weeks[f.name]; const full = w.filter(x => x >= f.perWeek).length / w.length * 100;
      out.flex.push({ name: f.name, perWeek: f.perWeek, avg: w.reduce((a, b) => a + b, 0) / w.length, full });
    }
    for (const wd of [...new Set((sc.water || []).map(x => x.name))]) { const s = r.stat[wd] || [0, 0]; out.water.push({ name: wd, pct: s[1] ? 100 * s[0] / s[1] : NaN }); }
    if (r.stat.heating) out.water.push({ name: "heating", pct: 100 * r.stat.heating[0] / r.stat.heating[1] });
    const N = r.N, a = r.acc;
    out.daily = {
      heatIn: (a.pv + a.trough) * N / 365, pv: a.pv * N / 365, trough: a.trough * N / 365, cook: a.cook * N / 365,
      surplus: (a.cart + a.bonus) * N / 365, loss: a.loss * N / 365, cascade: a.cascade * N / 365, flat: a.flat * N / 365,
      divert: a.divert * N / 365, loop: a.loop * N / 365, jacket: a.jacket * N / 365, water: a.water * N / 365, away: a.away * N / 365, pvSpill: a.pvSpill * N / 365
    };
    out.pasteurL = a.divert * N / 365 / (20 * CPW * 42 / 3600) * 20;     // litres a day, 20 L drums 30 -> 72 C
    out.cart = r.cartN * N; out.bonus = r.bonusN * N;
    out.minMeal = Math.min(...out.loads.map(x => x.pct).filter(x => !isNaN(x)), 100);
    out.minFlex = Math.min(...out.flex.map(x => x.full), 100);
    out.minT = r.minT; out.minSoc = r.minSoc * 100; out.balance = r.balance; out.saltKg = r.saltKg * N;
    return out;
  }

  // smallest number of modules that meets the targets
  function autoSize(sc, cfg, climate, target) {
    const tg = target || { meal: 95, flex: 90 };
    let last = null;
    for (let n = 1; n <= 80; n++) {
      const r = run(sc, Object.assign({}, cfg, { modules: n }), climate), s = summarize(r);
      last = { n, r, s };
      if (s.minMeal >= tg.meal && s.minFlex >= tg.flex) return last;
    }
    return Object.assign(last, { notMet: true });
  }

  const API = { run, summarize, autoSize, makeClimate, PROFILES, Store, RECEIVERS, rng };
  if (typeof module !== "undefined" && module.exports) module.exports = API; else root.ABEngine = API;
})(typeof window !== "undefined" ? window : globalThis);
