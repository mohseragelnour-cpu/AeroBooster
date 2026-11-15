/* AeroBooster revision C – scenario simulator UI. Uses ABEngine (engine.js) and ABScenarios (scenarios.js). */
(function () {
  "use strict";
  const E = window.ABEngine, SC = window.AB_SCENARIOS, GE = window.ABGeom;
  const $ = (id) => document.getElementById(id);
  const BASE = { Tmax: 255, Gstore: 0.289, jacket: 0.6, tankMax: 75, ctrlPvW: 100, egFrac: 0 };
  const AR = { tea: "غلي الشاي", frying: "القلي", breakfast: "الفطور", main: "الغداء", evening: "العشاء", kisra: "الكسرة", oven: "الفرن والخبز",
    washing: "ماء الغسيل 45°م", hygiene: "ماء الاستحمام 60°م", heating: "تدفئة الشتاء", dishwater: "ماء الأواني", cleaning: "ماء التنظيف", process: "حرارة التصنيع" };
  const MONTHS = ["ينا", "فبر", "مار", "أبر", "ماي", "يون", "يول", "أغس", "سبت", "أكت", "نوف", "ديس"];
  const PROFILE_AR = { sahel_dry: "ساحل جاف (نوع الخرطوم)", sahel_rain: "ساحل بموسم أمطار طويل (نوع الأبيض/نيالا)", coastal: "ساحل حار رطب (نوع بورتسودان)", temperate40: "معتدل نحو 40° شمالًا (نوع سومقايت/أبشرون)" };
  const CITIES = [["الخرطوم", 15.59, 32.53, "sahel_dry"], ["عطبرة", 17.70, 33.98, "sahel_dry"], ["ود مدني", 14.40, 33.52, "sahel_dry"], ["الأبيض", 13.18, 30.22, "sahel_rain"],
    ["نيالا", 12.05, 24.88, "sahel_rain"], ["كسلا", 15.45, 36.40, "sahel_rain"], ["بورتسودان", 19.62, 37.22, "coastal"], ["سومقايت", 40.59, 49.67, "temperate40"]];

  // ------------------------------------------------------------------ artwork (inline SVG, no remote images)
  const LOGO = `<svg width="64" height="64" viewBox="0 0 64 64" aria-label="AeroBooster">
    <circle cx="32" cy="32" r="31" fill="#fff7ed"/><g stroke="#eda100" stroke-width="3" stroke-linecap="round">
    ${[0, 45, 90, 135, 180, 225, 270, 315].map(a => { const r = a * Math.PI / 180; return `<line x1="${32 + 17 * Math.cos(r)}" y1="${22 + 17 * Math.sin(r)}" x2="${32 + 22 * Math.cos(r)}" y2="${22 + 22 * Math.sin(r)}"/>`; }).join("")}</g>
    <circle cx="32" cy="22" r="11" fill="#f59e0b"/><rect x="18" y="34" width="28" height="22" rx="6" fill="#c2410c"/>
    <rect x="22" y="40" width="20" height="12" rx="3" fill="#fed7aa"/><path d="M28 50c-3-4 2-6 0-10 5 3 6 7 4 10z" fill="#ea580c"/></svg>`;
  const sky = (c) => `<rect width="160" height="84" fill="${c || "#e8f1fb"}"/><circle cx="138" cy="16" r="9" fill="#f6b73c"/><rect y="70" width="160" height="14" fill="#e9dcc3"/>`;
  const panel = (x, y, w) => `<g transform="translate(${x},${y}) skewX(-18)"><rect width="${w}" height="12" fill="#1e3a5c"/><path d="M${w / 3} 0v12M${2 * w / 3} 0v12M0 6h${w}" stroke="#7fa6d6" stroke-width=".8"/></g>`;
  const box = (x, y) => `<rect x="${x}" y="${y}" width="14" height="16" rx="3" fill="#c2410c"/><rect x="${x + 3}" y="${y + 4}" width="8" height="6" rx="1.5" fill="#fed7aa"/>`;
  const ICONS = {
    kiosk: `<svg viewBox="0 0 160 84">${sky()}${panel(40, 18, 56)}<rect x="36" y="34" width="70" height="30" rx="4" fill="#d97706"/><rect x="36" y="30" width="70" height="6" fill="#92400e"/>
      <circle cx="50" cy="68" r="6" fill="#333"/><circle cx="92" cy="68" r="6" fill="#333"/>${box(60, 40)}<path d="M84 44h12v12h-12z" fill="#555"/><path d="M96 46c5 0 5 7 0 7" stroke="#555" fill="none" stroke-width="2"/>
      <path d="M88 40c-2-4 2-5 0-9M92 40c-2-4 2-5 0-9" stroke="#999" fill="none"/></svg>`,
    smallhouse: `<svg viewBox="0 0 160 84">${sky()}<path d="M50 44l26-20 26 20z" fill="#9a3412"/>${panel(60, 28, 30)}<rect x="54" y="44" width="44" height="26" fill="#fde68a"/><rect x="70" y="54" width="10" height="16" fill="#92400e"/>${box(108, 52)}</svg>`,
    house: `<svg viewBox="0 0 160 84">${sky()}<path d="M34 42l40-26 40 26z" fill="#9a3412"/>${panel(46, 24, 56)}<rect x="40" y="42" width="68" height="28" fill="#fde68a"/><rect x="66" y="52" width="12" height="18" fill="#92400e"/><rect x="48" y="50" width="10" height="9" fill="#93c5fd"/><rect x="88" y="50" width="10" height="9" fill="#93c5fd"/>${box(120, 52)}</svg>`,
    shared: `<svg viewBox="0 0 160 84">${sky()}<path d="M14 46l28-20 28 20zM78 40l34-24 34 24z" fill="#9a3412"/>${panel(22, 30, 34)}${panel(88, 22, 46)}<rect x="18" y="46" width="48" height="24" fill="#fde68a"/><rect x="82" y="40" width="60" height="30" fill="#fcd34d"/><rect x="36" y="56" width="10" height="14" fill="#92400e"/><rect x="106" y="54" width="12" height="16" fill="#92400e"/></svg>`,
    communal: `<svg viewBox="0 0 160 84">${sky()}${panel(20, 14, 120)}<rect x="22" y="30" width="116" height="40" fill="#e7e5e4"/><ellipse cx="58" cy="54" rx="20" ry="6" fill="#57534e"/><rect x="38" y="54" width="40" height="12" fill="#57534e"/>
      <ellipse cx="104" cy="54" rx="20" ry="6" fill="#57534e"/><rect x="84" y="54" width="40" height="12" fill="#57534e"/><path d="M52 46c-3-5 3-6 0-11M104 46c-3-5 3-6 0-11" stroke="#a8a29e" fill="none" stroke-width="2"/></svg>`,
    cafe: `<svg viewBox="0 0 160 84">${sky()}${panel(30, 16, 90)}<rect x="28" y="32" width="104" height="38" fill="#fef3c7"/><path d="M28 32h104l-6 8H34z" fill="#b45309"/><path d="M62 48h22v14a6 6 0 0 1-6 6h-10a6 6 0 0 1-6-6z" fill="#fff" stroke="#78350f" stroke-width="2"/>
      <path d="M84 52c7 0 7 9 0 9" stroke="#78350f" fill="none" stroke-width="2"/><path d="M68 44c-2-4 2-5 0-8M76 44c-2-4 2-5 0-8" stroke="#a16207" fill="none"/></svg>`,
    bakery: `<svg viewBox="0 0 160 84">${sky("#fdf2e4")}${panel(26, 14, 100)}<path d="M30 70V44a50 22 0 0 1 100 0v26z" fill="#b45309"/><path d="M58 70V54a22 12 0 0 1 44 0v16z" fill="#1c1917"/><path d="M64 66c4-8 28-8 32 0z" fill="#f59e0b"/>
      <path d="M70 54c-2-4 2-5 0-9M88 54c-2-4 2-5 0-9" stroke="#fb923c" fill="none" stroke-width="2"/></svg>`,
    factory: `<svg viewBox="0 0 160 84">${sky()}<path d="M20 70V40l24 12V40l24 12V40l24 12V30h14v40z" fill="#64748b"/><rect x="96" y="12" width="10" height="20" fill="#475569"/>${panel(110, 34, 40)}${panel(110, 50, 40)}${box(26, 54)}${box(50, 54)}</svg>`
  };

  // ------------------------------------------------------------------ unit prices (USD, editable; sources in the cost tab)
  const PRICES = [
    ["pvW", "ألواح كهروضوئية (دولار/واط، تسليم الموقع)", 0.35],
    ["mountW", "حوامل وكوابل الألواح (دولار/واط)", 0.10],
    ["heater", "سخان مغمور + متحكم تيار مستمر (دولار/وحدة)", 120],
    ["saltKg", "ملح نترات 60/40 (دولار/كغم)", 1.0],
    ["vesselL", "وعاء المخزن من الفولاذ والغلاف الخارجي (دولار/لتر)", 3.5],
    ["troughM2", "حوض متتبّع + مستقبل (دولار/m²)", 150],
    ["flatM2", "مجمِّع ماء مسطح (دولار/m²)", 120],
    ["tankL", "خزان ماء معزول + صمام (دولار/لتر)", 2.0],
    ["ctrl", "لوح 100 W + بطارية 1.2 kWh + إلكترونيات (دولار/وحدة)", 300],
    ["cook", "سطح طبخ وصاج وفرن ملحق وخراطيش (دولار/وحدة)", 150],
    ["heaterKw", "مخزن مركزي: سخانات ومتحكمات (دولار/kWp)", 90],
    ["tankBigL", "مخزن مركزي: خزان ماء كبير (دولار/لتر)", 1.2],
    ["oilLoop", "مخزن مركزي: مضخة زيت حراري وخزان تمدد وصمامات وزيت (دولار)", 1550],
    ["pipeM", "مخزن مركزي: أنابيب زيت معزولة (دولار/م)", 40],
    ["station", "مخزن مركزي: محطة طبخ بمبادل حراري (دولار/محطة)", 300],
    ["labour", "تصنيع وتركيب (% من المعدات)", 20],
    ["years", "عمر الحساب (سنة)", 15],
    ["lpgKg", "سعر غاز الطبخ للمقارنة (دولار/كغم)", 1.2]
  ];
  const price = {}; PRICES.forEach(p => price[p[0]] = p[2]);
  const isCentral = () => !!(st.sc.plant && $("arch").value === "central");
  // central plant: one big store; heat loss scales with surface and thicker insulation (x0.6), meals via a thermal-oil loop, bakes on the store
  function plantCfg(p, storeL, tankL, insul) {
    return { stations: p.stations, maxOutKw: p.maxOutKw, loopLossKw: p.loopLossKw, loopDT: p.loopDT, bakeDirect: true, cartsPerDay: p.cartsPerDay,
      Gstore: GE.geom(storeL, true, insul || p.insul).G, insul: insul || p.insul, cascKw: Math.max(1, (tankL || p.tankL) / 120), central: true, pipeM: p.pipeM };
  }
  function costOf(cfg, saltKgPerUnit) {
    if (cfg.central) {
      const P = price, kwp = cfg.pvM2 * 0.215;
      const items = { pv: kwp * 1000 * (P.pvW + P.mountW), heater: kwp * P.heaterKw, salt: saltKgPerUnit * P.saltKg,
        vessel: 45 * P.vesselL * Math.pow(cfg.storeL / 45, 2 / 3) * 1.6, trough: cfg.troughM2 * P.troughM2, flat: cfg.flatM2 * P.flatM2,
        insul: GE.geom(cfg.storeL, true, cfg.insul).insUsd, tank: cfg.tankL * P.tankBigL, oil: P.oilLoop + (cfg.pipeM || 20) * P.pipeM, stations: (cfg.stations || 1) * P.station, ctrl: P.ctrl + 300 };
      const hw = Object.values(items).reduce((a, b) => a + b, 0);
      return { items, hw, unit: hw * (1 + P.labour / 100), total: hw * (1 + P.labour / 100) };
    }
    const kwp = cfg.pvM2 * 0.215, P = price;
    const items = {
      pv: kwp * 1000 * (P.pvW + P.mountW), heater: cfg.pvM2 ? P.heater : 0, salt: saltKgPerUnit * P.saltKg, vessel: cfg.storeL * P.vesselL,
      insul: GE.geom(cfg.storeL, false, cfg.insul || "rw200").insUsd, trough: cfg.troughM2 * P.troughM2, flat: cfg.flatM2 * P.flatM2, tank: cfg.tankL * P.tankL, ctrl: P.ctrl, cook: P.cook
    };
    const hw = Object.values(items).reduce((a, b) => a + b, 0);
    return { items, hw, unit: hw * (1 + P.labour / 100), total: hw * (1 + P.labour / 100) * cfg.modules };
  }
  // useful heat a year (kWh) and LPG it replaces: 13.8 kWh/kg, 50 % stove efficiency (assumed)
  function valueOf(s) {
    const useful = (s.daily.cook + s.daily.surplus + s.daily.water + s.daily.divert) * 365;
    const lpgKg = (s.daily.cook + s.daily.surplus) * 365 / (13.8 * 0.5);
    return { useful, lpgKg, lpgUsd: lpgKg * price.lpgKg };
  }

  // ------------------------------------------------------------------ state
  const st = { sc: SC[2], photos: {}, power: null, last: null, matrix: null };
  const sliders = [["N", "vN", v => v + " وحدة"], ["pv", "vPv", v => v + " m² ≈ " + (v * 0.215).toFixed(2) + " kWp"], ["tr", "vTr", v => v + " m²"], ["st", "vSt", v => v + " L"],
    ["fl", "vFl", v => v], ["tk", "vTk", v => v], ["hi", "vHi", v => v], ["lo", "vLo", v => v], ["ki", "vKi", v => v], ["ov", "vOv", v => v], ["cl", "vCl", v => v]];
  const showVals = () => {
    sliders.forEach(([i, o, f]) => { $(o).textContent = f(+$(i).value); });
    if (!$("insul").value) return;
    const c = isCentral(), g = GE.geom(+$("st").value, c, $("insul").value);
    $("geomLine").textContent = c ? `صندوق داخلي ${fmt(g.L, 2)}×${fmt(g.W, 2)}×${fmt(g.H, 2)} م، خارجي ${fmt(g.Lo, 2)}×${fmt(g.Wo, 2)}×${fmt(g.Ho, 2)} م، ${fmt(g.weight)} كغم مع الملح، فقد ${fmt(g.G, 2)} W/K`
      : `أسطوانة داخلية ⌀${fmt(g.D * 100)}×${fmt(g.H * 100)} سم، خارجية ⌀${fmt(g.Do * 100)}×${fmt(g.Ho * 100)} سم، ${fmt(g.weight)} كغم مع الملح، فقد ${fmt(g.G, 2)} W/K`;
  };

  function initControls() {
    $("logo").innerHTML = LOGO;
    const sel = $("profile");
    sel.innerHTML = CITIES.map((c, i) => `<option value="c${i}">${c[0]} – ${PROFILE_AR[c[3]]}</option>`).join("") +
      Object.keys(E.PROFILES).map(k => `<option value="p_${k}">مناخ عام: ${PROFILE_AR[k] || E.PROFILES[k].label}</option>`).join("");
    sel.onchange = () => {
      const v = sel.value;
      if (v[0] === "c") { const c = CITIES[+v.slice(1)]; $("lat").value = c[1]; $("lon").value = c[2]; }
      st.power = null; setStatus("locStatus", "مناخ مدمج: " + sel.options[sel.selectedIndex].text + ". (اضغط NASA POWER لبيانات الأقمار الصناعية للموقع.)");
      updateLink(); run();
    };
    ["lat", "lon"].forEach(id => $(id).onchange = () => { st.power = null; updateLink(); });
    sliders.forEach(([i]) => $(i).oninput = showVals);
    $("mode").onchange = () => { const m = $("mode").value; if (m === "pv") $("tr").value = 0; if (m === "trough") { $("pv").value = 0; if (+$("tr").value === 0) $("tr").value = 6; }
      if (m === "hybrid") { if (+$("tr").value === 0) $("tr").value = 3; if (+$("pv").value === 0) $("pv").value = 4; } showVals(); };
    $("btnRun").onclick = run; $("btnAuto").onclick = auto; $("btnReset").onclick = () => { loadScenario(st.sc); run(); };
    $("arch").onchange = () => { loadScenario(st.sc); run(); };
    $("insul").innerHTML = Object.keys(GE.INSUL).map(k => `<option value="${k}">${GE.INSUL[k].ar}</option>`).join("");
    $("insul").onchange = showVals; $("st").addEventListener("input", showVals);
    document.querySelectorAll("#dtabs .tab").forEach(t => t.onclick = () => { document.querySelectorAll("#dtabs .tab").forEach(x => x.classList.remove("on")); t.classList.add("on"); renderDrawing(t.dataset.d); });
    $("btnWater").onclick = waterMatrix; $("wMetric").onchange = renderWater;
    $("btnGps").onclick = gps; $("btnPower").onclick = fetchPower; $("btnPaste").onclick = pastePower;
    $("btnMatrix").onclick = matrix; $("btnCopy").onclick = copyText;
    $("photo").onchange = (e) => { const f = e.target.files[0]; if (!f) return; try { st.photos[st.sc.id] = URL.createObjectURL(f); } catch (x) {} renderCards(); };
    document.querySelectorAll("#tabs .tab").forEach(t => t.onclick = () => { document.querySelectorAll("#tabs .tab").forEach(x => x.classList.remove("on")); t.classList.add("on"); renderTab(); });
    updateLink(); renderCards(); loadScenario(st.sc);
  }
  function setStatus(id, txt, cls) { const el = $(id); el.textContent = txt; el.className = "status" + (cls ? " " + cls : ""); }
  function powerUrl() {
    const la = (+$("lat").value).toFixed(3), lo = (+$("lon").value).toFixed(3);
    return `https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_DNI,T2M,T2M_MAX,T2M_MIN&community=RE&longitude=${lo}&latitude=${la}&format=JSON`;
  }
  function updateLink() { const a = $("powerLink"), u = powerUrl(); a.href = u; a.textContent = u; }

  function renderCards() {
    $("scen").innerHTML = SC.map(s => `<div class="sc${s === st.sc ? " on" : ""}" data-id="${s.id}">${st.photos[s.id] ? `<img src="${st.photos[s.id]}" alt="">` : ICONS[s.icon]}<b>${s.title}</b><small>${s.en}</small></div>`).join("");
    document.querySelectorAll(".sc").forEach(c => c.onclick = () => { st.sc = SC.find(s => s.id === c.dataset.id); renderCards(); loadScenario(st.sc); run(); });
  }
  function setRanges(central) {
    const R = central ? { st: [200, 3000, 50], pv: [10, 250, 1], fl: [0, 40, 1], tk: [100, 3000, 50] } : { st: [20, 90, 5], pv: [0, 12, 0.5], fl: [0, 4, 0.5], tk: [40, 300, 10] };
    for (const k in R) { $(k).min = R[k][0]; $(k).max = R[k][1]; $(k).step = R[k][2]; }
    $("N").disabled = central;
  }
  function loadScenario(s) {
    $("archBox").style.display = s.plant ? "block" : "none";
    const central = !!(s.plant && $("arch").value === "central");
    setRanges(central);
    const h = central ? Object.assign({}, s.hw, s.plant, { modules: 1, troughM2: 0 }) : s.hw;
    $("N").value = h.modules; $("pv").value = h.pvM2; $("tr").value = h.troughM2 || 0; $("st").value = h.storeL; $("fl").value = h.flatM2; $("tk").value = h.tankL;
    $("mode").value = h.troughM2 > 0 && h.pvM2 > 0 ? "hybrid" : h.troughM2 > 0 ? "trough" : "pv";
    $("insul").value = h.insul || (central ? "rw250" : "rw200");
    $("hi").value = 245; $("lo").value = 140; $("cl").value = 7; $("surplus").checked = true; $("rec").value = "expected";
    const fk = (s.flex || []).find(f => f.name === "kisra"), fo = (s.flex || []).find(f => f.name === "oven");
    $("ki").value = fk ? fk.perWeek : 0; $("ki").disabled = !fk; $("ov").value = fo ? fo.perWeek : 0; $("ov").disabled = !fo;
    $("scNote").innerHTML = `<b>${s.title}:</b> ${s.who}.${s.note ? " " + s.note : ""}`;
    showVals();
  }
  function cfgNow() {
    const c = cfgSmall();
    if (isCentral()) { Object.assign(c, plantCfg(st.sc.plant, c.storeL, c.tankL, $("insul").value), { modules: 1 }); }
    return c;
  }
  function cfgSmall() {
    const ins = $("insul").value || "rw200";
    return Object.assign({}, BASE, { insul: ins, Gstore: GE.geom(+$("st").value, false, ins).G, modules: +$("N").value, pvM2: +$("pv").value, troughM2: +$("tr").value, storeL: +$("st").value, flatM2: +$("fl").value, tankL: +$("tk").value,
      thrHi: +$("hi").value, thrLo: Math.min(+$("lo").value, +$("hi").value - 20), cleanDays: +$("cl").value, surplus: $("surplus").checked, receiver: $("rec").value });
  }
  function scNow() {
    const s = Object.assign({}, st.sc);
    s.flex = (st.sc.flex || []).map(f => Object.assign({}, f, { perWeek: f.name === "kisra" ? +$("ki").value : f.name === "oven" ? +$("ov").value : f.perWeek })).filter(f => f.perWeek > 0);
    return s;
  }
  function climateNow() {
    const v = $("profile").value, lat = +$("lat").value;
    let prof = v.startsWith("p_") ? v.slice(2) : CITIES[+v.slice(1)][3];
    return E.makeClimate({ lat, profile: prof, seed: 7, storm: $("storm").checked, power: st.power });
  }

  // ------------------------------------------------------------------ location and satellite data
  function nearestProfile(lat) {
    const a = Math.abs(lat);
    if (a > 30) return "temperate40"; if (a < 14) return "sahel_rain"; return "sahel_dry";
  }
  function gps() {
    if (!navigator.geolocation) { setStatus("locStatus", "هذا المتصفح لا يوفر الموقع. أدخل خط العرض والطول يدويًا.", "err"); return; }
    setStatus("locStatus", "جارٍ طلب الموقع من الجهاز…");
    try {
      navigator.geolocation.getCurrentPosition(p => {
        $("lat").value = p.coords.latitude.toFixed(3); $("lon").value = p.coords.longitude.toFixed(3);
        $("profile").value = "p_" + nearestProfile(p.coords.latitude); st.power = null; updateLink();
        setStatus("locStatus", `الموقع: ${p.coords.latitude.toFixed(3)}, ${p.coords.longitude.toFixed(3)} (دقة ±${Math.round(p.coords.accuracy)} م). جارٍ جلب بيانات NASA POWER…`, "ok");
        fetchPower();
      }, err => setStatus("locStatus", "تعذّر الحصول على الموقع (" + err.message + "). داخل صفحة claude.ai يُمنع الموقع؛ افتح الملف المحمّل في المتصفح، أو أدخل الإحداثيات يدويًا.", "err"),
      { enableHighAccuracy: false, timeout: 12000, maximumAge: 600000 });
    } catch (e) { setStatus("locStatus", "الموقع ممنوع في هذه الصفحة. أدخل الإحداثيات يدويًا.", "err"); }
  }
  function parsePower(j) {
    const p = j && j.properties && j.properties.parameter;
    if (!p || !p.ALLSKY_SFC_SW_DWN) throw new Error("صيغة غير متوقعة");
    const keys = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
    const g = (n) => p[n] ? keys.map(k => p[n][k]) : null;
    const ghi = g("ALLSKY_SFC_SW_DWN"), dni = g("ALLSKY_SFC_SW_DNI"), t = g("T2M"), tmax = g("T2M_MAX"), tmin = g("T2M_MIN");
    if (ghi.some(x => !(x > 0))) throw new Error("قيم إشعاع ناقصة");
    const ok = (a) => a && a.every(x => x > -100);
    const out = { ghi, dni: ok(dni) && dni.every(x => x >= 0) ? dni : null, t: ok(t) ? t : E.PROFILES.sahel_dry.T, tmax: ok(tmax) ? tmax : null, tmin: ok(tmin) ? tmin : null };
    if (j.geometry && j.geometry.coordinates) { $("lon").value = (+j.geometry.coordinates[0]).toFixed(3); $("lat").value = (+j.geometry.coordinates[1]).toFixed(3); }
    return out;
  }
  function usePower(pw, src) {
    st.power = pw; $("profile").value = "p_" + nearestProfile(+$("lat").value);
    const yr = pw.ghi.reduce((a, b) => a + b, 0) / 12;
    setStatus("locStatus", `${src}: متوسط الإشعاع ${yr.toFixed(2)} kWh/m²/يوم` + (pw.dni ? `، الإشعاع المباشر ${(pw.dni.reduce((a, b) => a + b, 0) / 12).toFixed(2)}` : "") + `، الحرارة ${(pw.t.reduce((a, b) => a + b, 0) / 12).toFixed(1)}°م. أيام الطقس مولَّدة لتطابق هذه المتوسطات الشهرية.`, "ok");
    run();
  }
  async function fetchPower() {
    const b = $("btnPower"); b.disabled = true; updateLink();
    setStatus("locStatus", "جارٍ جلب بيانات NASA POWER (متوسطات الأقمار الصناعية الشهرية)…");
    try {
      const ctl = typeof AbortController !== "undefined" ? new AbortController() : null;
      const tm = setTimeout(() => ctl && ctl.abort(), 20000);
      const r = await fetch(powerUrl(), ctl ? { signal: ctl.signal } : {});
      clearTimeout(tm);
      if (!r.ok) throw new Error("HTTP " + r.status);
      usePower(parsePower(await r.json()), "NASA POWER للموقع " + $("lat").value + ", " + $("lon").value);
    } catch (e) {
      setStatus("locStatus", "تعذّر الاتصال بـ NASA POWER (" + (e.message || e) + "). صفحة claude.ai تمنع الاتصال بمواقع أخرى: افتح الملف المحمّل في متصفحك، أو افتح الرابط في الأسفل والصق النتيجة. يُستعمل المناخ المدمج الآن.", "err");
    } finally { b.disabled = false; }
  }
  function pastePower() {
    try { usePower(parsePower(JSON.parse($("powerPaste").value)), "بيانات NASA ملصقة"); }
    catch (e) { setStatus("locStatus", "لم أستطع قراءة النص الملصق: " + e.message + ". انسخ صفحة الرابط كاملة.", "err"); }
  }

  // ------------------------------------------------------------------ run and render
  const cls = (p, a, b) => p >= (a || 95) ? "good" : p >= (b || 85) ? "mid" : "bad";
  const fmt = (x, d) => (x === undefined || isNaN(x)) ? "–" : x.toLocaleString("en-US", { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 });
  function busy(on) { $("prog").style.display = on ? "block" : "none"; $("prog").firstElementChild.style.width = on ? "60%" : "0"; ["btnRun", "btnAuto", "btnMatrix"].forEach(i => $(i).disabled = on); }
  function run() {
    busy(true);
    setTimeout(() => {
      try {
        const sc = scNow(), cfg = cfgNow(), cl = climateNow();
        const r = E.run(sc, cfg, cl), s = E.summarize(r);
        st.last = { r, s, sc, cfg, cl }; renderKpis(); renderTab();
      } catch (e) { $("tabBody").innerHTML = `<div class="status err">خطأ في المحاكاة: ${e.message}</div>`; }
      busy(false);
    }, 20);
  }
  function centralPv(sc, cfg, cl) {
    const okp = (a) => { const s = E.summarize(E.run(sc, Object.assign({}, cfg, { pvM2: a }), cl)); return s.minMeal >= 95 && s.minFlex >= 90; };
    let lo = 5, hi = 300; if (!okp(hi)) return { pv: hi, notMet: true };
    while (hi - lo > 1) { const m = Math.round((lo + hi) / 2); if (okp(m)) hi = m; else lo = m; }
    return { pv: hi };
  }
  function auto() {
    busy(true);
    if (isCentral()) { setTimeout(() => { const a = centralPv(scNow(), cfgNow(), climateNow()); $("pv").value = a.pv; showVals(); busy(false); run();
      if (a.notMet) setStatus("locStatus", "حتى 300 m² لا تكفي بهذا المخزن. كبّر المخزن أو خفف الجدول.", "err"); }, 20); return; }
    setTimeout(() => {
      const a = E.autoSize(scNow(), cfgNow(), climateNow(), { meal: 95, flex: 90 });
      $("N").value = a.n; showVals(); busy(false); run();
      if (a.notMet) setStatus("locStatus", "حتى 80 وحدة لا تحقق الهدف بهذه التجهيزات. زد الألواح أو المخزن أو خفف الجدول.", "err");
    }, 20);
  }
  function renderKpis() {
    const { s, cfg, r } = st.last, N = cfg.modules;
    const flexTxt = s.flex.length ? s.flex.map(f => `${AR[f.name]} ${fmt(f.full)}%`).join(" · ") : "لا يوجد خبز";
    const k = [
      [fmt(s.minMeal) + "%", "أدنى خدمة للوجبات والأحمال الثابتة", cls(s.minMeal)],
      [s.flex.length ? fmt(s.minFlex) + "%" : "–", "أسابيع اكتمل فيها جدول الخبز: " + flexTxt, s.flex.length ? cls(s.minFlex, 90, 75) : ""],
      [cfg.central ? "مركزي" : N + "", (cfg.central ? fmt(cfg.storeL) + " لتر · " : "عدد الوحدات · ") + fmt(N * cfg.pvM2 * 0.215, 1) + " kWp ألواح" + (cfg.troughM2 ? " · " + fmt(N * cfg.troughM2) + " m² حوض" : ""), ""],
      [fmt(s.saltKg) + " kg", "ملح شمسي (60/40) في " + fmt(N * cfg.storeL) + " لتر", ""],
      [fmt(s.daily.heatIn, 1) + " kWh", "حرارة تدخل المخازن في اليوم", ""],
      [fmt(s.daily.cook, 1) + " kWh", "حرارة للطبخ والخبز في اليوم", ""],
      [fmt(s.pasteurL) + " L", "ماء شرب مبستر في اليوم من الفائض", ""],
      [fmt(s.cart) + " / " + fmt(s.bonus), "خراطيش محمولة / خبزات إضافية في السنة", ""],
      [fmt(r.minT) + "°م", "أدنى حرارة للمخزن خلال السنة", r.minT < 100 ? "mid" : ""],
      ["$" + fmt(costOf(cfg, r.saltKg).total), "تكلفة تقديرية للموقع (معدات + تصنيع)", ""],
      ["$" + fmt(costOf(cfg, r.saltKg).total / (valueOf(s).useful * price.years), 3), "تكلفة الكيلوواط ساعة المفيد على " + price.years + " سنة · يوفّر ≈ " + fmt(valueOf(s).lpgKg) + " كغم غاز/سنة", ""],
      [Math.abs(s.balance) < 1e-3 ? "✓" : fmt(s.balance, 3), "توازن الطاقة (الفرق kWh)", Math.abs(s.balance) < 1e-3 ? "good" : "bad"]
    ];
    $("kpis").innerHTML = k.map(([v, l, c]) => `<div class="kpi"><div class="v ${c}">${v}</div><div class="l">${l}</div></div>`).join("");
  }
  function barRow(name, pct, extra) {
    const c = pct >= 95 ? "#15803d" : pct >= 85 ? "#d97706" : "#b91c1c";
    return `<tr><td>${name}</td><td style="width:45%"><div class="bar"><i style="width:${Math.max(0, Math.min(100, pct))}%;background:${c}"></i></div></td><td class="n">${fmt(pct, 1)}%</td><td style="font-size:11.5px;color:#52514e">${extra || ""}</td></tr>`;
  }
  function renderTab() {
    if (!st.last) return;
    const t = document.querySelector("#tabs .tab.on").dataset.t, { s, cfg, r, sc } = st.last, N = cfg.modules, B = $("tabBody");
    const cl = Object.assign({}, st.last.cl, { label: st.power ? "بيانات NASA POWER الشهرية للموقع (أيام مولَّدة تطابقها)" : (PROFILE_AR[Object.keys(E.PROFILES).find(k => E.PROFILES[k].label === st.last.cl.label)] || st.last.cl.label) + " – مناخ تركيبي مدمج" });
    if (t === "service") {
      let h = `<table><tr><th>الحمل</th><th>نسبة الخدمة</th><th></th><th>ملاحظة</th></tr>`;
      s.loads.forEach(l => h += barRow(AR[l.name] || l.name, l.pct, "من مرات الحمل في السنة"));
      s.flex.forEach(f => h += barRow(AR[f.name] + ` (${f.perWeek}/أسبوع)`, f.full, `متوسط ${fmt(f.avg, 2)} مرة في الأسبوع`));
      s.water.forEach(w => h += barRow(AR[w.name] || w.name, w.pct, w.name === "heating" ? "ساعات التدفئة المخدومة" : "يُحسب فقط إن كان الخزان ساخنًا بما يكفي"));
      B.innerHTML = h + `</table><div class="note">الحمل لا يُحسب مخدومًا إلا إذا كانت حرارة المخزن فوق حدّه الأدنى (150°م للطبخ، 215°م للكسرة، 235°م للفرن). الكسرة والفرن يُجدولان مرنًا داخل نافذتهما ولا يعملان معًا.</div>`;
    } else if (t === "energy") {
      const d = s.daily, rows = [["حرارة من الألواح إلى المخزن", d.pv, "#eda100"], ["حرارة من الحوض المتتبّع", d.trough, "#c2410c"], ["طبخ وخبز", d.cook, "#7c2d12"],
        ["خراطيش وخبزة إضافية (فائض)", d.surplus, "#ea580c"], ["فقد المخزن (عزل)", d.loss, "#a8a29e"], ["من المخزن إلى خزان الماء", d.cascade, "#60a5fa"],
        ["مجمِّع الماء إلى الخزان", d.flat, "#2a78d6"], ["فائض المجمِّع للبسترة/التجفيف", d.divert, "#0e7490"], ["ماء ساخن وتدفئة مستهلكة", d.water, "#1e40af"]];
      const mx = Math.max(...rows.map(x => x[1]), 0.1);
      B.innerHTML = `<svg class="chart" viewBox="0 0 720 ${rows.length * 34 + 20}" font-family="Cairo" font-size="13" direction="ltr">` + rows.map((x, i) => {
        const y = 10 + i * 34, w = 390 * x[1] / mx;
        return `<text x="712" y="${y + 17}" text-anchor="end" fill="#1d1c1a">${x[0]}</text><rect x="${468 - w}" y="${y + 4}" width="${Math.max(w, 1)}" height="18" rx="4" fill="${x[2]}"><title>${fmt(x[1], 2)} kWh/يوم</title></rect><text x="${462 - w}" y="${y + 18}" text-anchor="end" fill="#52514e">${fmt(x[1], 1)}</text>`;
      }).join("") + `</svg><div class="note">قيم متوسطة لكل يوم للموقع كله (kWh). ${d.pvSpill > 0.05 ? `فائض ألواح لم يُخزَّن: ${fmt(d.pvSpill, 1)} kWh/يوم يمكن تشغيل حمل كهربائي به.` : ""}</div>`;
    } else if (t === "boq") {
      if (cfg.central) {
        const kwp = cfg.pvM2 * 0.215, it = [
          ["ألواح كهروضوئية", `${cfg.pvM2} m² ≈ ${fmt(kwp, 1)} kWp`], ["سخانات مقاومة مغمورة + متحكمات تيار مستمر (مجموعات ≈3 kW)", `${fmt(kwp * 0.92, 1)} kW في ${Math.ceil(kwp / 3)} مجموعة`],
          ["مخزن ملحي مركزي معزول 200 مم (صوف صخري/ألياف سيراميك)", `${fmt(cfg.storeL)} L`], ["ملح NaNO₃/KNO₃ 60/40", `${fmt(r.saltKg)} kg`],
          ["ألواح صاج وفرن مثبتة على المخزن مباشرة (بلا مبادل)", "للكسرة والخبز"], ["دائرة زيت حراري: مضخة، خزان تمدد، صمامات، أنابيب معزولة", `${cfg.pipeM} م، قدرة ${cfg.maxOutKw} kW`],
          ["محطات طبخ بمبادل زيت (قدور، صاج قلي)", `${cfg.stations} محطة`], ["مجمِّعات ماء مسطحة", `${cfg.flatM2} m²`], ["خزان ماء ساخن + صمام 75°م", `${fmt(cfg.tankL)} L`],
          ["متحكم + بطارية 2.4 kWh للمضخة ليلًا", "1"], ["خراطيش محمولة لتوزيع الفائض", `${cfg.cartsPerDay} يوميًا`]];
        B.innerHTML = `<table><tr><th>البند (مخزن مركزي واحد)</th><th>الكمية</th></tr>` + it.map(x => `<tr><td>${x[0]}</td><td class="n">${x[1]}</td></tr>`).join("") +
          `</table><div class="note">الوجبات تصل عبر دائرة الزيت وتحتاج المخزن أسخن بـ ${cfg.loopDT}°م من حد الطبخ؛ لذلك الصاج والفرن فوق المخزن نفسه، لأن الخبز يحتاج 235–248°م والمخزن حده 255°م. المساحة ≈ ${fmt(cfg.pvM2 * 1.6 + cfg.flatM2 * 1.3 + 15)} m².</div>`;
        return;
      }
      const per = r.saltKg, kwp = cfg.pvM2 * 0.215, htr = Math.max(0.3, Math.round(kwp * 0.92 * 10) / 10);
      const items = [
        ["ألواح كهروضوئية", cfg.pvM2 ? `${cfg.pvM2} m² (≈${fmt(kwp, 2)} kWp)` : "–", cfg.pvM2 ? `${fmt(N * kwp, 1)} kWp` : "–"],
        ["سخان مقاومة مغمور في الملح + متحكم MPPT للسخان", cfg.pvM2 ? `${fmt(htr, 1)} kW` : "–", cfg.pvM2 ? `${N} قطعة` : "–"],
        ["حوض قطع مكافئ متتبّع ومستقبل مفرغ", cfg.troughM2 ? `${cfg.troughM2} m²` : "–", cfg.troughM2 ? `${fmt(N * cfg.troughM2)} m²` : "–"],
        ["مخزن ملحي معزول (فولاذ لا يصدأ، صوف صخري + غطاء)", `${cfg.storeL} L`, `${fmt(N * cfg.storeL)} L`],
        ["ملح شمسي NaNO₃/KNO₃ 60/40", `${fmt(per)} kg`, `${fmt(per * N)} kg`],
        ["مجمِّع ماء مسطح", `${cfg.flatM2} m²`, `${fmt(N * cfg.flatM2, 1)} m²`],
        ["خزان ماء ساخن + صمام تحويل 75°م", `${cfg.tankL} L`, `${fmt(N * cfg.tankL)} L`],
        ["لوح المتحكم 100 W + بطارية 1.2 kWh", "1", `${N}`],
        ["خراطيش محمولة + صندوق حفظ الحرارة", "2", `${2 * N}`],
        ["سطح طبخ وصاج كسرة وفرن ملحق", "1", `${N}`]];
      B.innerHTML = `<table><tr><th>البند</th><th>لكل وحدة</th><th>للموقع (${N} وحدة)</th></tr>` + items.map(x => `<tr><td>${x[0]}</td><td class="n">${x[1]}</td><td class="n">${x[2]}</td></tr>`).join("") +
        `</table><div class="note">كميات تقديرية من النموذج، بلا أسعار. المساحة اللازمة على السطح أو الأرض ≈ ${fmt(N * (cfg.pvM2 * 1.6 + cfg.troughM2 * 2 + cfg.flatM2 * 1.3))} m² مع المسافات.</div>`;
    } else if (t === "cost") {
      const c = costOf(cfg, r.saltKg), v = valueOf(s), names = { pv: "ألواح + حوامل", heater: "سخان + متحكم", salt: "ملح", vessel: "وعاء المخزن والعزل", trough: "حوض متتبّع", flat: "مجمِّع الماء", tank: "خزان الماء", ctrl: "متحكم وبطارية", cook: "أدوات الطبخ والخبز", oil: "دائرة الزيت الحراري", stations: "محطات الطبخ", insul: "عزل المخزن" };
      let h = `<div class="row" style="gap:16px;flex-wrap:wrap"><div style="flex:1;min-width:280px"><table><tr><th>البند (لكل وحدة)</th><th>دولار</th></tr>` +
        Object.keys(c.items).filter(k => c.items[k] > 0).map(k => `<tr><td>${names[k]}</td><td class="n">${fmt(c.items[k])}</td></tr>`).join("") +
        `<tr><td>تصنيع وتركيب ${price.labour}%</td><td class="n">${fmt(c.unit - c.hw)}</td></tr><tr><th>الوحدة</th><th class="n">${fmt(c.unit)}</th></tr><tr><th>الموقع (${cfg.central ? "مخزن مركزي" : N + " وحدة"})</th><th class="n">${fmt(c.total)}</th></tr></table>
        <table style="margin-top:10px"><tr><td>حرارة مفيدة في السنة (طبخ، خراطيش، ماء، بسترة)</td><td class="n">${fmt(v.useful)} kWh</td></tr>
        <tr><td>تكلفة الكيلوواط ساعة المفيد على ${price.years} سنة (بلا خصم وبلا صيانة)</td><td class="n">$${fmt(c.total / (v.useful * price.years), 3)}</td></tr>
        <tr><td>غاز طبخ يُستغنى عنه (طبخ وخراطيش فقط)</td><td class="n">${fmt(v.lpgKg)} kg/سنة ≈ ${fmt(v.lpgKg / 12.5, 1)} أسطوانة 12.5 كغم</td></tr>
        <tr><td>قيمته بسعر ${price.lpgKg} $/كغم</td><td class="n">$${fmt(v.lpgUsd)}/سنة</td></tr>
        <tr><th>استرداد بسيط من الغاز وحده</th><th class="n">${v.lpgUsd > 0 ? fmt(c.total / v.lpgUsd, 1) + " سنة" : "–"}</th></tr></table></div>
        <div style="flex:1;min-width:280px"><b style="font-size:12.5px">أسعار الوحدة (عدّلها لسوقك)</b><table>` +
        PRICES.map(p => `<tr><td style="font-size:12px">${p[1]}</td><td style="width:90px"><input type="number" step="any" data-p="${p[0]}" value="${price[p[0]]}" style="padding:4px 6px"></td></tr>`).join("") + `</table></div></div>
        <div class="note">الأسعار الافتراضية تقديرات بالدولار من أسواق عالمية (2026) مع هامش للشحن، وليست عروض أسعار. مراجع: ألواح الوحدات بالجملة نحو 0.20–0.40 دولار/واط (pv magazine، BloombergNEF)؛ نترات البوتاسيوم نحو 0.6–1.1 دولار/كغم ونترات الصوديوم نحو 1.1–1.3 دولار/كغم (IMARC، Intratec)؛ بطاريات ليثيوم فوسفات الحديد الصغيرة نحو 160–230 دولار/kWh بالتجزئة. بنود الوعاء والسخان والحوض والتصنيع تقديرات للتصنيع المحلي يجب التحقق منها بعروض فعلية. الاسترداد يحسب الغاز فقط، ولا يحسب الماء الساخن والمبستر.</div>`;
      B.innerHTML = h;
      B.querySelectorAll("input[data-p]").forEach(inp => inp.onchange = () => { const x = parseFloat(inp.value); if (!isNaN(x) && x >= 0) { price[inp.dataset.p] = x; renderKpis(); renderTab(); if (st.matrix) renderMatrix(); } });
    } else if (t === "year") {
      const W = 720, H = 260, x0 = 40, y0 = 20, pw = W - 60, ph = H - 50, Tmin = 0, Tmx = 270;
      const X = d => x0 + pw * d / 364, Y = T => y0 + ph * (1 - (T - Tmin) / (Tmx - Tmin));
      const line = (k, c) => `<polyline fill="none" stroke="${c}" stroke-width="1.6" points="${r.daily.map((p, d) => X(d).toFixed(1) + "," + Y(p[k]).toFixed(1)).join(" ")}"/>`;
      let g = ""; for (const T of [0, 75, 140, 200, 240]) g += `<line x1="${x0}" x2="${x0 + pw}" y1="${Y(T)}" y2="${Y(T)}" stroke="#e3e1da"/><text x="${x0 - 5}" y="${Y(T) + 4}" text-anchor="end" font-size="11" fill="#8a8984">${T}</text>`;
      const heavy = r.daily.map((p, d) => p.dty === "heavy" ? `<rect x="${X(d) - 1}" y="${y0}" width="2.2" height="${ph}" fill="#cbd5e1" opacity=".7"/>` : "").join("");
      const ml = MONTHS.map((m, i) => `<text x="${X(i * 30.4 + 15)}" y="${H - 12}" text-anchor="middle" font-size="11" fill="#52514e">${m}</text>`).join("");
      B.innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" font-family="Cairo" direction="ltr">${g}${heavy}<rect x="${x0}" y="${Y(255)}" width="${pw}" height="${Y(220) - Y(255)}" fill="#fde7d6" opacity=".5"/>${line("T", "#c2410c")}${line("Tw", "#2a78d6")}${ml}
        <text x="${x0 + 6}" y="${Y(262)}" font-size="11" fill="#c2410c">حرارة المخزن الملحي آخر اليوم °م</text><text x="${x0 + 6}" y="${Y(85)}" font-size="11" fill="#2a78d6">خزان الماء °م</text></svg>
        <div class="note">الشريط البرتقالي الفاتح: مجال انصهار الملح 220–230°م وحتى 255°م. الخطوط الرمادية: أيام غائمة كثيفة أو غبار. ${cl.label}.</div>`;
    } else {
      const m = new Array(12).fill(0), dn = new Array(12).fill(0), n = new Array(12).fill(0), ty = { clear: 0, hazy: 0, partly: 0, heavy: 0 };
      const mo = d => Math.min(11, Math.floor(d / 30.42));
      for (let d = 0; d < 365; d++) { const k0 = mo(d); n[k0]++; ty[cl.dayType[d]]++; for (let k = 0; k < 96; k++) { const w = cl.at(d, k); m[k0] += w.ghi * 0.25 / 1000; dn[k0] += w.dniN * 0.25 / 1000; } }
      const g = m.map((x, i) => x / n[i]), dd = dn.map((x, i) => x / n[i]), mx = Math.max(...g, ...dd, 1) * 1.08;
      const W = 720, H = 240, bw = 22;
      let bars = ""; g.forEach((v, i) => { const x = 50 + i * 55, h1 = 170 * v / mx, h2 = 170 * dd[i] / mx;
        bars += `<rect x="${x}" y="${200 - h1}" width="${bw}" height="${h1}" rx="3" fill="#eda100"><title>GHI ${fmt(v, 2)}</title></rect><rect x="${x + bw + 2}" y="${200 - h2}" width="${bw}" height="${h2}" rx="3" fill="#c2410c"><title>DNI ${fmt(dd[i], 2)}</title></rect><text x="${x + bw / 2}" y="${196 - h1}" text-anchor="middle" font-size="10" fill="#52514e">${fmt(v, 1)}</text><text x="${x + bw * 1.5 + 2}" y="${196 - h2}" text-anchor="middle" font-size="10" fill="#52514e">${fmt(dd[i], 1)}</text><text x="${x + bw}" y="218" text-anchor="middle" font-size="11">${MONTHS[i]}</text>`; });
      B.innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" font-family="Cairo" direction="ltr"><line x1="40" x2="700" y1="200" y2="200" stroke="#ccc"/>${bars}
        <rect x="520" y="10" width="12" height="12" fill="#eda100"/><text x="538" y="21" font-size="12">إشعاع أفقي كلي</text><rect x="520" y="28" width="12" height="12" fill="#c2410c"/><text x="538" y="39" font-size="12">إشعاع مباشر</text></svg>
        <div class="note">kWh/m²/يوم كما يراها النموذج. أيام السنة: صافية ${ty.clear}، مغبرة ${ty.hazy}، غائمة جزئيًا ${ty.partly}، غائمة كثيفة ${ty.heavy}. المصدر: ${cl.label}.</div>`;
    }
  }

  // ------------------------------------------------------------------ matrix of all scenarios
  function matrix() {
    busy(true); const out = [], cl = climateNow(); let i = 0;
    const cfg0 = cfgSmall(); if (isCentral()) { cfg0.pvM2 = 6; cfg0.troughM2 = 0; cfg0.storeL = 45; }
    const jobs = []; SC.forEach(s0 => { jobs.push([s0, false]); if (s0.plant) jobs.push([s0, true]); });
    $("matrix").innerHTML = `<div class="status">جارٍ الحساب… 0/${jobs.length}</div>`;
    const step = () => {
      if (i >= jobs.length) { st.matrix = out; renderMatrix(); busy(false); return; }
      const [s0, central] = jobs[i];
      if (central) {
        const p = s0.plant, cfg = Object.assign({}, cfg0, { storeL: p.storeL, flatM2: p.flatM2, tankL: p.tankL, troughM2: 0, modules: 1 }, plantCfg(p, p.storeL, p.tankL, p.insul));
        const a = centralPv(s0, cfg, cl); cfg.pvM2 = a.pv;
        const r = E.run(s0, cfg, cl); out.push({ sc: s0, central: true, n: 1, s: E.summarize(r), r, cfg, notMet: a.notMet });
      } else {
        const cfg = Object.assign({}, cfg0, { storeL: s0.hw.storeL, flatM2: s0.hw.flatM2, tankL: s0.hw.tankL, Gstore: GE.geom(s0.hw.storeL, false, cfg0.insul).G });
        if (cfg0.pvM2 === 0 && cfg0.troughM2 === 0) cfg.pvM2 = s0.hw.pvM2;
        const a = E.autoSize(s0, cfg, cl, { meal: 95, flex: 90 });
        out.push({ sc: s0, n: a.n, s: a.s, r: a.r, cfg, notMet: a.notMet });
      }
      i++; $("matrix").innerHTML = `<div class="status">جارٍ الحساب… ${i}/${jobs.length}</div>`; setTimeout(step, 10);
    };
    setTimeout(step, 20);
  }
  function renderMatrix() {
    const rows = st.matrix;
    let h = `<table><tr><th>السيناريو</th><th>وحدات</th><th>ألواح kWp</th><th>حوض m²</th><th>ملح kg</th><th>أدنى وجبة</th><th>أسابيع خبز كاملة</th><th>طبخ kWh/يوم</th><th>ماء مبستر L/يوم</th><th>خراطيش/سنة</th><th>تكلفة تقديرية $</th><th>$/kWh مفيد</th></tr>`;
    for (const x of rows) {
      const c = x.cfg;
      h += `<tr${x.central ? ' style="background:#effaf2"' : ""}><td>${x.sc.title}${x.central ? " – <b>مخزن مركزي " + fmt(x.cfg.storeL) + " L</b>" : ""}${x.notMet ? " ⚠" : ""}</td><td class="n"><b>${x.central ? "1 مركزي" : x.n}</b></td><td class="n">${fmt(x.n * c.pvM2 * 0.215, 1)}</td><td class="n">${fmt(x.n * c.troughM2)}</td><td class="n">${fmt(x.s.saltKg)}</td>
        <td class="n ${cls(x.s.minMeal)}">${fmt(x.s.minMeal)}%</td><td class="n ${x.s.flex.length ? cls(x.s.minFlex, 90, 75) : ""}">${x.s.flex.length ? fmt(x.s.minFlex) + "%" : "–"}</td>
        <td class="n">${fmt(x.s.daily.cook, 1)}</td><td class="n">${fmt(x.s.pasteurL)}</td><td class="n">${fmt(x.s.cart)}</td><td class="n">${fmt(costOf(Object.assign({}, c, { modules: x.n }), x.r.saltKg).total)}</td><td class="n">${fmt(costOf(Object.assign({}, c, { modules: x.n }), x.r.saltKg).total / (valueOf(x.s).useful * price.years), 3)}</td></tr>`;
    }
    $("matrix").innerHTML = h + `</table><div class="note">الوحدة الصغيرة بالتجهيزات المختارة أعلاه (${isCentral() ? 6 : cfgSmall().pvM2} m² ألواح، ${isCentral() ? 0 : cfgSmall().troughM2} m² حوض) مع مخزن وخزان كل سيناريو. ⚠ = لم يتحقق الهدف حتى 80 وحدة. الصفوف الخضراء: مخزن مركزي واحد بحجم ثابت، والألواح محسوبة لأصغر مساحة تحقق الهدف في هذا الموقع.</div>`;
  }

  function resultText() {
    if (!st.last) return "";
    const { s, cfg, cl, sc } = st.last, L = [];
    L.push(`AeroBooster rev C – ${sc.en} | ${sc.title}`, `Location ${$("lat").value}, ${$("lon").value} | climate: ${cl.label}`,
      `Modules ${cfg.modules} | PV ${cfg.pvM2} m2 | trough ${cfg.troughM2} m2 | store ${cfg.storeL} L | flat ${cfg.flatM2} m2 | tank ${cfg.tankL} L | thresholds ${cfg.thrHi}/${cfg.thrLo} C`);
    L.push("load,service %"); s.loads.forEach(l => L.push(`${l.name},${fmt(l.pct, 1)}`)); s.flex.forEach(f => L.push(`${f.name} full weeks (${f.perWeek}/wk),${fmt(f.full, 1)}`)); s.water.forEach(w => L.push(`${w.name},${fmt(w.pct, 1)}`));
    L.push(`estimated cost USD,${fmt(costOf(cfg, st.last.r.saltKg).total)}`, `LPG avoided kg/yr,${fmt(valueOf(s).lpgKg)}`);
    L.push(`heat in kWh/day,${fmt(s.daily.heatIn, 2)}`, `cooking kWh/day,${fmt(s.daily.cook, 2)}`, `pasteurized L/day,${fmt(s.pasteurL)}`, `cartridges/yr,${s.cart}`, `salt kg,${fmt(s.saltKg)}`);
    if (st.matrix) { L.push("", "scenario,modules,kWp,trough m2,salt kg,min meal %,full bake weeks %,pasteurized L/day,cost USD");
      st.matrix.forEach(x => L.push(`${x.sc.en}${x.central ? " (central " + x.cfg.storeL + " L)" : ""},${x.n},${fmt(x.n * x.cfg.pvM2 * 0.215, 1)},${x.n * x.cfg.troughM2},${fmt(x.s.saltKg)},${fmt(x.s.minMeal)},${x.s.flex.length ? fmt(x.s.minFlex) : "-"},${fmt(x.s.pasteurL)},${fmt(costOf(Object.assign({}, x.cfg, { modules: x.n }), x.r.saltKg).total)}`)); }
    L.push("", "Simulated results, synthetic or NASA POWER-calibrated weather. Not measured. CC BY 4.0, doi:10.5281/zenodo.24154141");
    return L.join("\n");
  }
  function copyText() {
    const t = resultText();
    const fallback = () => { let ta = $("copyBox"); if (!ta) { ta = document.createElement("textarea"); ta.id = "copyBox"; ta.rows = 8; ta.style.cssText = "width:100%;margin-top:8px;direction:ltr;font-size:11px"; $("btnCopy").parentNode.after(ta); }
      ta.value = t; ta.focus(); ta.select(); };
    try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(() => { $("btnCopy").textContent = "✓ نُسخ"; setTimeout(() => $("btnCopy").textContent = "⧉ نسخ النتائج نصًا", 1500); }, fallback); else fallback(); }
    catch (e) { fallback(); }
  }

  // ------------------------------------------------------------------ 6. schematic drawings (inline SVG)
  function renderDrawing(kind) {
    const D = kind === "central" ? DRAW_CENTRAL() : DRAW_MODULE();
    $("drawing").innerHTML = D;
  }
  const defs = `<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="#f5efe3"/><line x1="0" y1="0" x2="0" y2="8" stroke="#d6c7a6" stroke-width="3"/></pattern>
    <linearGradient id="salt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fdba74"/><stop offset=".45" stop-color="#fb923c"/><stop offset="1" stop-color="#c2410c"/></linearGradient>
    ${[["ar", "#52514e"], ["arR", "#dc2626"], ["arB", "#2563eb"], ["arT", "#0e7490"], ["arO", "#ea580c"], ["arY", "#ca8a04"]].map(([id, c]) => `<marker id="${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="${c}"/></marker>`).join("")}</defs>`;
  const tag = (x, y, n) => `<circle cx="${x}" cy="${y}" r="11" fill="#1e3a5c"/><text x="${x}" y="${y + 4}" text-anchor="middle" fill="#fff" font-size="12" font-weight="700">${n}</text>`;
  const pv = (x, y, w, h) => `<g transform="translate(${x},${y}) skewX(-20)"><rect width="${w}" height="${h}" fill="#1e3a5c" stroke="#0f2238"/>${[1, 2, 3, 4, 5].map(i => `<line x1="${w * i / 6}" y1="0" x2="${w * i / 6}" y2="${h}" stroke="#6b93c4" stroke-width=".8"/>`).join("")}<line x1="0" y1="${h / 2}" x2="${w}" y2="${h / 2}" stroke="#6b93c4" stroke-width=".8"/></g>`;
  const flat = (x, y, w, h) => `<g transform="translate(${x},${y}) skewX(-20)"><rect width="${w}" height="${h}" fill="#dbeafe" stroke="#2a78d6" stroke-width="2"/>${[1, 2, 3, 4, 5, 6, 7].map(i => `<line x1="${w * i / 8}" y1="3" x2="${w * i / 8}" y2="${h - 3}" stroke="#2a78d6" stroke-width="1.5"/>`).join("")}</g>`;
  const legend = (items, x0, y0, cols, cw) => items.map((t, i) => { const x = x0 + (i % cols) * cw, y = y0 + Math.floor(i / cols) * 22; return `${tag(x + cw - 14, y, i + 1)}<text x="${x + cw - 30}" y="${y + 4}" text-anchor="end" font-size="12.5" fill="#1d1c1a">${t}</text>`; }).join("");
  function DRAW_MODULE() {
    const g = GE.geom(45, false, "rw200");
    return `<svg class="chart" viewBox="0 0 980 760" font-family="Cairo" direction="ltr">${defs}
    <text x="960" y="28" text-anchor="end" font-size="16" font-weight="800">الوحدة المنزلية C.3 – مقطع رأسي (غير مقيس بدقة)</text>
    ${pv(60, 50, 220, 70)}${tag(50, 60, 1)}
    <rect x="70" y="200" width="150" height="70" rx="8" fill="#fff" stroke="#1e3a5c" stroke-width="2"/><text x="145" y="228" text-anchor="middle" font-size="12">متحكم السخان (تيار مستمر)</text><text x="145" y="248" text-anchor="middle" font-size="11" fill="#52514e">+ لوح 100 W وبطارية 1.2 kWh</text>${tag(60, 195, 2)}
    <path d="M150 122V200" stroke="#b91c1c" stroke-width="3" fill="none"/><path d="M220 235H360V300" stroke="#b91c1c" stroke-width="3" fill="none"/>
    <rect x="300" y="240" width="260" height="330" rx="10" fill="url(#hatch)" stroke="#a8a29e" stroke-width="2"/>
    <rect x="345" y="290" width="170" height="240" rx="6" fill="url(#salt)" stroke="#57534e" stroke-width="3"/>
    <line x1="345" y1="360" x2="515" y2="360" stroke="#fff" stroke-dasharray="5 4" opacity=".8"/><text x="430" y="352" text-anchor="middle" font-size="11" fill="#7c2d12">ملح منصهر ≥230°م</text><text x="430" y="420" text-anchor="middle" font-size="11" fill="#fff">ملح شمسي 60/40 · ${fmt(g.salt)} كغم</text>
    <rect x="356" y="300" width="8" height="200" fill="#7f1d1d"/>${tag(372, 470, 3)}
    <path d="M495 310l-14 12 14 12-14 12 14 12-14 12 14 12-14 12 14 12" stroke="#1d4ed8" stroke-width="3" fill="none"/>${tag(470, 440, 4)}
    <rect x="335" y="270" width="190" height="18" rx="3" fill="#292524"/><ellipse cx="430" cy="266" rx="70" ry="6" fill="#d6a76a"/>${tag(545, 268, 5)}
    <path d="M315 245L420 175L535 182" stroke="#78716c" stroke-width="10" fill="none" stroke-linecap="round" opacity=".55"/><text x="440" y="168" text-anchor="middle" font-size="11" fill="#52514e">غطاء معزول يُرفع عند الطبخ</text>
    <rect x="566" y="380" width="80" height="70" rx="6" fill="#fde68a" stroke="#b45309" stroke-width="2"/><text x="606" y="420" text-anchor="middle" font-size="11">فرن ملحق</text>${tag(656, 380, 6)}
    <path d="M296 300v240M290 300v240" stroke="#60a5fa" stroke-width="3"/>${tag(278, 520, 7)}
    <rect x="150" y="420" width="90" height="50" rx="6" fill="#fff" stroke="#c2410c" stroke-width="2"/><text x="195" y="450" text-anchor="middle" font-size="11">خرطوشة</text>${tag(140, 420, 8)}
    <path d="M300 445H244" stroke="#c2410c" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#arO)"/>
    ${flat(700, 50, 200, 80)}${tag(690, 60, 9)}
    <rect x="770" y="260" width="110" height="200" rx="40" fill="#eff6ff" stroke="#2a78d6" stroke-width="3"/><text x="825" y="360" text-anchor="middle" font-size="12">خزان ماء</text><text x="825" y="378" text-anchor="middle" font-size="11" fill="#52514e">120 لترًا ≤75°م</text>${tag(890, 270, 10)}
    <path d="M760 132L800 256" stroke="#2a78d6" stroke-width="3" fill="none" marker-end="url(#arB)"/><path d="M860 256L880 132" stroke="#2a78d6" stroke-width="3" fill="none" marker-end="url(#arR)"/>
    <path d="M509 315H640V300H766" stroke="#dc2626" stroke-width="3" fill="none" marker-end="url(#arR)"/><path d="M770 430H680V505H513" stroke="#2563eb" stroke-width="3" fill="none" marker-end="url(#arB)"/>
    <rect x="628" y="288" width="28" height="22" fill="#fff" stroke="#111" stroke-width="2"/><path d="M628 288l28 22M656 288l-28 22" stroke="#111"/>${tag(642, 270, 11)}
    <path d="M290 540V625H700V470H766" stroke="#60a5fa" stroke-width="2.5" fill="none" stroke-dasharray="6 4" marker-end="url(#arB)"/>
    <rect x="860" y="520" width="100" height="60" rx="8" fill="#ecfeff" stroke="#0e7490" stroke-width="2"/><text x="910" y="548" text-anchor="middle" font-size="11">مبستِر ماء الشرب</text><text x="910" y="566" text-anchor="middle" font-size="10" fill="#52514e">65°م لست دقائق</text>
    <path d="M880 460V516" stroke="#0e7490" stroke-width="3" marker-end="url(#arT)"/><circle cx="880" cy="488" r="9" fill="#fff" stroke="#0e7490" stroke-width="2"/>${tag(905, 488, 12)}
    <path d="M800 462V560H760" stroke="#2a78d6" stroke-width="3" fill="none" marker-end="url(#arB)"/><text x="752" y="564" text-anchor="end" font-size="11">صنابير 45–60°م</text>
    <line x1="300" y1="585" x2="560" y2="585" stroke="#52514e" marker-start="url(#ar)" marker-end="url(#ar)"/>
    <text x="420" y="604" text-anchor="end" font-size="11" fill="#52514e">داخلي / خارجي (سم):</text><text x="428" y="604" font-size="11" fill="#52514e" direction="ltr">⌀${fmt(g.D * 100)} × ${fmt(g.H * 100)}  /  ⌀${fmt(g.Do * 100)} × ${fmt(g.Ho * 100)}</text>
    ${legend(["ألواح 6.5 m² ≈ 1.4 kWp", "متحكم السخان والإلكترونيات", "سخان مقاومة مغمور 1.2 kW", "ملف تسخين الماء من المخزن (قاعدة النافذتين)", "صاج الكسرة على غطاء المخزن", "فرن ملحق بجانب المخزن", "غلاف ماء يستعيد فقد المخزن", "خراطيش حرارة محمولة من الفائض", "مجمِّع ماء مسطح 2 m²", "خزان ماء 120 لترًا", "صمام النافذتين 245/140°م", "صمام تحويل 75°م إلى المبستر"], 20, 660, 3, 320)}
    </svg><div class="note">الأحمر: كهرباء وماء ساخن ذاهب، الأزرق: ماء عائد. عزل 200 مم صوف صخري يعطي فقدًا ≈${fmt(g.G, 2)} W/K؛ النسخة C افترضت 0.29 W/K وهذا يحتاج نحو 100 مم ميكروبوري غالي الثمن. الرسم توضيحي للمبدأ وليس رسمًا تصنيعيًا.</div>`;
  }
  function DRAW_CENTRAL() {
    const p = SC.find(s => s.id === "communal").plant, g = GE.geom(p.storeL, true, p.insul);
    return `<svg class="chart" viewBox="0 0 1000 720" font-family="Cairo" direction="ltr">${defs}
    <text x="980" y="28" text-anchor="end" font-size="16" font-weight="800">المخزن المركزي للمطبخ الجماعي C.3 – مقطع (غير مقيس بدقة)</text>
    ${pv(40, 50, 90, 55)}${pv(150, 50, 90, 55)}${pv(260, 50, 90, 55)}${tag(32, 58, 1)}<text x="200" y="128" text-anchor="middle" font-size="11" fill="#52514e">${p.pvM2} m² ≈ ${fmt(p.pvM2 * 0.215, 1)} kWp في مجموعات</text>
    <rect x="70" y="160" width="220" height="56" rx="8" fill="#fff" stroke="#1e3a5c" stroke-width="2"/><text x="200" y="185" text-anchor="end" font-size="12">مجموعات السخان:</text><text x="206" y="185" font-size="12" direction="ltr">${Math.ceil(p.pvM2 * 0.215 / 3)} × ≈3 kW</text><text x="180" y="204" text-anchor="middle" font-size="11" fill="#52514e">متحكم تيار مستمر لكل مجموعة</text>${tag(62, 158, 2)}
    <path d="M180 108V160M140 216V330M180 216V330M220 216V330" stroke="#b91c1c" stroke-width="3" fill="none"/>
    <rect x="80" y="300" width="460" height="250" rx="10" fill="url(#hatch)" stroke="#a8a29e" stroke-width="2"/>
    <rect x="120" y="340" width="380" height="170" rx="6" fill="url(#salt)" stroke="#57534e" stroke-width="3"/>
    ${[140, 180, 220].map(x => `<rect x="${x - 4}" y="335" width="8" height="150" fill="#7f1d1d"/>`).join("")}${tag(240, 470, 3)}
    <text x="330" y="430" text-anchor="middle" font-size="12" fill="#fff">${fmt(p.storeL)} لتر · ${fmt(g.salt)} كغم ملح</text>
    <path d="M270 495h220" stroke="#facc15" stroke-width="5"/><path d="M270 488h220" stroke="#facc15" stroke-width="2"/>${tag(300, 515, 4)}
    <rect x="115" y="318" width="390" height="20" fill="#292524"/>
    ${[160, 250, 340].map(x => `<ellipse cx="${x}" cy="314" rx="38" ry="5" fill="#d6a76a"/>`).join("")}${tag(110, 290, 5)}
    <rect x="405" y="250" width="95" height="68" rx="6" fill="#fde68a" stroke="#b45309" stroke-width="2"/><text x="452" y="288" text-anchor="middle" font-size="11">فرن على المخزن</text>${tag(512, 250, 6)}
    <path d="M490 495H600V420" stroke="#ca8a04" stroke-width="4" fill="none"/><circle cx="600" cy="400" r="18" fill="#fff" stroke="#ca8a04" stroke-width="3"/><path d="M592 400h16M600 392v16" stroke="#ca8a04" stroke-width="2"/>${tag(628, 392, 7)}
    <rect x="575" y="300" width="50" height="40" rx="6" fill="#fef9c3" stroke="#ca8a04" stroke-width="2"/><text x="600" y="324" text-anchor="middle" font-size="9">تمدد</text><path d="M600 340V382" stroke="#ca8a04" stroke-width="2"/>${tag(640, 300, 8)}
    <path d="M618 400H960" stroke="#ea580c" stroke-width="4" marker-end="url(#arO)"/><path d="M960 470H560V515H494" stroke="#ca8a04" stroke-width="3" fill="none" stroke-dasharray="7 4" marker-end="url(#arY)"/>
    ${[700, 790, 880].map((x, i) => `<path d="M${x} 400V430" stroke="#ea580c" stroke-width="3"/><path d="M${x - 30} 430h60l-6 34h-48z" fill="#57534e"/><path d="M${x + 20} 464V470" stroke="#ca8a04" stroke-width="3"/>`).join("")}${tag(940, 440, 9)}
    <text x="790" y="390" text-anchor="middle" font-size="11" fill="#52514e">زيت حراري ≤270°م · ${p.maxOutKw} kW · ${p.stations} محطات</text>
    ${flat(640, 60, 140, 60)}${flat(800, 60, 140, 60)}${tag(632, 68, 10)}<text x="800" y="140" text-anchor="middle" font-size="11" fill="#52514e">${p.flatM2} m² مجمِّعات ماء</text>
    <rect x="690" y="560" width="200" height="110" rx="40" fill="#eff6ff" stroke="#2a78d6" stroke-width="3"/><text x="790" y="610" text-anchor="middle" font-size="12">خزان ماء ${fmt(p.tankL)} لتر</text><text x="790" y="630" text-anchor="middle" font-size="11" fill="#52514e">≤75°م</text>${tag(900, 565, 11)}
    <path d="M700 122C660 300 660 400 700 560M900 122C960 300 940 450 880 560" stroke="#2a78d6" stroke-width="2.5" fill="none" marker-end="url(#arB)"/>
    <path d="M150 550V600H686" stroke="#dc2626" stroke-width="3" fill="none" marker-end="url(#arR)"/><rect x="380" y="588" width="28" height="22" fill="#fff" stroke="#111" stroke-width="2"/><path d="M380 588l28 22M408 588l-28 22" stroke="#111"/>${tag(430, 590, 12)}
    <path d="M76 310V640H690" stroke="#60a5fa" stroke-width="2.5" fill="none" stroke-dasharray="6 4"/>${tag(66, 470, 13)}
    <rect x="560" y="660" width="110" height="44" rx="8" fill="#ecfeff" stroke="#0e7490" stroke-width="2"/><text x="615" y="687" text-anchor="middle" font-size="11">مبستِر / مجفف</text><path d="M690 650H674" stroke="#0e7490" stroke-width="3" marker-end="url(#arT)"/>
    <rect x="320" y="200" width="150" height="44" rx="8" fill="#fff" stroke="#1e3a5c" stroke-width="2"/><text x="395" y="226" text-anchor="middle" font-size="11">متحكم + بطارية 2.4 kWh</text>${tag(480, 200, 14)}
    <text x="190" y="572" text-anchor="end" font-size="11" fill="#52514e">داخلي / خارجي (م):</text><text x="198" y="572" font-size="11" fill="#52514e" direction="ltr">${fmt(g.L, 2)} × ${fmt(g.W, 2)} × ${fmt(g.H, 2)}  /  ${fmt(g.Lo, 2)} × ${fmt(g.Wo, 2)} × ${fmt(g.Ho, 2)}  ·  ${fmt(g.weight)} kg</text>
    </svg>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:4px 14px;font-size:12px;margin-top:6px">${["ألواح كهروضوئية", "مجموعات السخانات ومتحكماتها", "سخانات مقاومة مغمورة", "ملف الزيت داخل الملح", "ألواح صاج على السطح مباشرة (بلا مبادل)", "فرن مثبت على المخزن", "مضخة الزيت الحراري", "خزان تمدد الزيت", "محطات طبخ بمبادل (قدور كبيرة، قلي)", "مجمِّعات ماء مسطحة", "خزان ماء كبير", "صمام النافذتين 245/140°م", "غلاف ماء يستعيد فقد المخزن", "متحكم وبطارية للمضخة ليلًا"].map((t, i) => `<div>${i + 1}. ${t}</div>`).join("")}</div>
    <div class="note">الصاج والفرن فوق المخزن مباشرة لأنهما يحتاجان 235–248°م، ولو مرّا عبر مبادل الزيت لاحتاج المخزن أكثر من حده 255°م. الوجبات (150°م) تمر عبر الزيت مع هامش 20°م. الرسم توضيحي للمبدأ وليس رسمًا تصنيعيًا.</div>`;
  }

  // ------------------------------------------------------------------ 7. store sizes for every category
  function sizeRows() {
    const rows = [];
    for (const s0 of SC) {
      rows.push({ sc: s0, central: false, N: s0.hw.modules, V: s0.hw.storeL, ins: s0.hw.insul || "rw200" });
      if (s0.plant) rows.push({ sc: s0, central: true, N: 1, V: s0.plant.storeL, ins: s0.plant.insul });
    }
    return rows;
  }
  function renderSizes() {
    let h = `<table><tr><th>الفئة</th><th>البنية</th><th>عدد المخازن</th><th>حجم المخزن L</th><th>ملح/مخزن kg</th><th>المقاس الداخلي</th><th>العزل</th><th>المقاس الخارجي</th><th>الوزن/مخزن kg</th><th>فقد W/K</th><th>طاقة 200→255°م kWh</th><th>سطح الطبخ m²</th><th>كثافة قدرة الخبز kW/m²</th></tr>`;
    for (const x of sizeRows()) {
      const g = GE.geom(x.V, x.central, x.ins), usable = E.Store(x.V, 0).usable;
      const bakeKw = Math.max(0, ...(x.sc.flex || []).map(f => f.kw / x.N));
      const flux = bakeKw / g.top, warn = flux > 4 ? " ⚠" : "";
      h += `<tr${x.central ? ' style="background:#effaf2"' : ""}><td>${x.sc.title}</td><td>${x.central ? "مركزي" : "وحدات"}</td><td class="n">${x.N}</td><td class="n">${fmt(x.V)}</td><td class="n">${fmt(g.salt)}</td>
        <td class="n">${x.central ? `${fmt(g.L, 2)}×${fmt(g.W, 2)}×${fmt(g.H, 2)} م` : `⌀${fmt(g.D * 100)}×${fmt(g.H * 100)} سم`}</td><td>${g.ins.ar}</td>
        <td class="n">${x.central ? `${fmt(g.Lo, 2)}×${fmt(g.Wo, 2)}×${fmt(g.Ho, 2)} م` : `⌀${fmt(g.Do * 100)}×${fmt(g.Ho * 100)} سم`}</td><td class="n">${fmt(g.weight)}</td><td class="n">${fmt(g.G, 2)}</td>
        <td class="n">${fmt(usable, 1)}${x.N > 1 ? ` (×${x.N} = ${fmt(usable * x.N)})` : ""}</td><td class="n">${fmt(g.top, 2)}</td><td class="n">${bakeKw ? fmt(flux, 1) + warn : "–"}</td></tr>`;
    }
    $("sizes").innerHTML = h + `</table><div class="note">الطاقة القابلة للاستعمال بين 200 و255°م تشمل الانصهار (220–230°م). الوزن يشمل الملح والوعاء الفولاذي والعزل. ⚠ كثافة قدرة فوق 4 kW/m² تحت الصاج تحتاج زعانف أو أنابيب حرارية في الملح تحت اللوح، ويجب قياسها في نموذج أولي؛ الملح الصلب تحت 220°م ضعيف التوصيل. خيارات العزل: صوف صخري (رخيص، k≈0.055 W/m·K)، أو ميكروبوري (k≈0.024 لكنه الأغلى ويتأثر بالرطوبة).</div>`;
  }

  // ------------------------------------------------------------------ 8. water collector x heat store matrix
  const WMULT = [0, 0.5, 1, 1.5, 2];
  function waterMatrix() {
    busy(true); const cl = climateNow(), rows = sizeRows(), out = []; let i = 0;
    const step = () => {
      if (i >= rows.length) { st.wmat = out; renderWater(); busy(false); return; }
      const x = rows[i], s0 = x.sc, hw = x.central ? s0.plant : s0.hw, cells = [];
      for (const m of WMULT) {
        const base = Object.assign({}, BASE, { thrHi: 245, thrLo: 140, cleanDays: 7, surplus: true, receiver: "expected", troughM2: 0 },
          x.central ? Object.assign({ modules: 1, storeL: hw.storeL, pvM2: hw.pvM2, tankL: hw.tankL }, plantCfg(hw, hw.storeL, hw.tankL, hw.insul))
                    : { modules: hw.modules, storeL: hw.storeL, pvM2: hw.pvM2, tankL: hw.tankL, insul: hw.insul, Gstore: GE.geom(hw.storeL, false, hw.insul).G });
        base.flatM2 = hw.flatM2 * m;
        const s = E.summarize(E.run(s0, base, cl));
        cells.push({ m, flat: base.flatM2 * (x.central ? 1 : hw.modules), casc: s.daily.cascade, jacket: s.daily.jacket, past: s.pasteurL, meal: s.minMeal,
          bake: s.flex.length ? s.minFlex : NaN, water: s.water.length ? Math.min(...s.water.map(w => w.pct)) : NaN });
      }
      out.push({ x, cells }); i++;
      $("wmatrix").innerHTML = `<div class="status">جارٍ الحساب… ${i}/${rows.length}</div>`; setTimeout(step, 10);
    };
    setTimeout(step, 20);
  }
  function renderWater() {
    if (!st.wmat) return;
    const k = $("wMetric").value, pct = ["water", "bake", "meal"].includes(k);
    let h = `<table><tr><th>الفئة</th><th>البنية</th>` + WMULT.map(m => `<th class="n">${m === 0 ? "بلا مجمِّع" : "×" + m}</th>`).join("") + `</tr>`;
    for (const r of st.wmat) {
      const vals = r.cells.map(c => c[k]), mx = Math.max(...vals.filter(v => !isNaN(v)), 1e-6);
      h += `<tr${r.x.central ? ' style="background:#effaf2"' : ""}><td>${r.x.sc.title}</td><td>${r.x.central ? "مركزي" : r.x.N + " وحدة"}</td>` + r.cells.map(c => {
        const v = c[k]; if (isNaN(v)) return `<td class="n">–</td>`;
        const bg = pct ? (v >= 95 ? "#dcfce7" : v >= 85 ? "#fef3c7" : "#fee2e2") : `rgba(42,120,214,${0.08 + 0.4 * v / mx})`;
        return `<td class="n" style="background:${bg}" title="${fmt(c.flat, 1)} m² مجمِّع">${fmt(v, pct ? 0 : 1)}${pct ? "%" : ""}<div style="font-size:10px;color:#52514e">${fmt(c.flat, 1)} m²</div></td>`;
      }).join("") + `</tr>`;
    }
    $("wmatrix").innerHTML = h + `</table><div class="note">كل خلية سنة كاملة للموقع الحالي بالتجهيزات الافتراضية للسيناريو؛ الرقم الصغير هو مساحة المجمِّع للموقع كله. بلا مجمِّع يأخذ الماء حرارته من المخزن الملحي فقط، فينافس الطبخ والخبز؛ مع المجمِّع تقل الحرارة المأخوذة من المخزن ويكبر الفائض الموجَّه للبسترة.</div>`;
  }

  // ------------------------------------------------------------------ 9. prototype P1 results -> design
  const P1 = { D: 0.30, Hv: 0.20, salt: 12, steelKg: 7.8 };
  function p1Geo(t) { const Ai = 2 * Math.PI * P1.D * P1.D / 4 + Math.PI * P1.D * P1.Hv, Do = P1.D + 2 * t, Ho = P1.Hv + 2 * t + 0.04;
    const Ao = 2 * Math.PI * Do * Do / 4 + Math.PI * Do * Ho; return 1.15 * Math.sqrt(Ai * Ao) / t; }       // G = k x this factor
  const p1S = E.Store(P1.salt, 0), Hst = T => p1S.H_of(T) + P1.steelKg * 0.5 * (T - 25);
  function Tof(H) { let lo = 20, hi = 320; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (Hst(m) < H) lo = m; else hi = m; } return (lo + hi) / 2; }
  function simCool(G, rows) { let H = Hst(rows[0].T), out = [rows[0].T];
    for (let i = 1; i < rows.length; i++) { const dt = (rows[i].t - rows[i - 1].t) * 60, T = Tof(H); H -= G * (T - rows[i - 1].Ta) * dt / 1000; out.push(Tof(H)); } return out; }
  function parseCsv(txt) {
    const L = txt.trim().split(/\r?\n/).filter(x => x.trim()); if (L.length < 3) throw new Error("السجل قصير");
    const h = L[0].split(",").map(x => x.trim().toLowerCase()), it = h.indexOf("time_min"), i2 = h.indexOf("t2"), i6 = h.indexOf("t6");
    if (it < 0 || i2 < 0) throw new Error("لا أجد العمودين time_min و T2");
    return L.slice(1).map(l => { const c = l.split(","); return { t: +c[it], T: +c[i2], Ta: i6 >= 0 && c[i6] !== "" ? +c[i6] : +$("pTa").value }; }).filter(r => isFinite(r.t) && isFinite(r.T));
  }
  let meas = null;
  function showMeas(G, src, extra) {
    const t = +$("pStage").value, k = G / p1Geo(t); meas = { G, k, t };
    const pvNeed = k <= 0.055 ? 6.5 : k <= 0.060 ? 7 : k <= 0.070 ? 7.5 : 8;   // home unit, 200 mm, three weather years (kpv.js)
    const verdict = k <= 0.055 ? ["good", "التصميم C.3 صالح: صوف صخري 200 مم و6.5 m² ألواح للمنزل."] : k <= 0.08 ? ["mid", `زد ألواح المنزل إلى ${pvNeed} m² أو العزل إلى 250 مم، وأعد حساب المصفوفة.`] : ["bad", "أعلى من المتوقع كثيرًا: افحص الفجوات والفلانجة ومنافذ السخان والتهوية، ثم أعد الاختبار T2."];
    $("pOut").className = "status " + (verdict[0] === "bad" ? "err" : "ok");
    $("pOut").innerHTML = `${src}: G = <b class="lt">${fmt(G, 3)} W/K</b> → موصلية العزل الفعلية k = <b class="lt">${fmt(k, 4)} W/m·K</b> (المفترض 0.055). ${extra || ""}<br><span class="${verdict[0]}">${verdict[1]}</span>`;
    $("btnApply").disabled = false;
  }
  function holdTest() { const dT = +$("pT").value - +$("pTa").value; if (!(dT > 20) || !(+$("pW").value > 0)) { $("pOut").textContent = "أدخل القدرة والحرارتين."; return; } showMeas(+$("pW").value / dT, "اختبار الإبقاء"); }
  function fitCool() {
    let rows; try { rows = parseCsv($("pCsv").value); } catch (e) { $("pOut").className = "status err"; $("pOut").textContent = e.message; return; }
    const sse = G => { const m = simCool(G, rows); return m.reduce((a, v, i) => a + (v - rows[i].T) ** 2, 0); };
    let lo = 0.05, hi = 3; for (let i = 0; i < 50; i++) { const a = lo + (hi - lo) * 0.382, b = lo + (hi - lo) * 0.618; if (sse(a) < sse(b)) hi = b; else lo = a; }
    const G = (lo + hi) / 2, m = simCool(G, rows), rms = Math.sqrt(sse(G) / rows.length);
    showMeas(G, "مطابقة منحنى التبريد", `فرق المطابقة ${fmt(rms, 2)} °م (أقل من 2 °م يعني أن النموذج يصف المخزن جيدًا).`);
    const W = 720, Hh = 220, t1 = rows.at(-1).t, Tmn = Math.min(...rows.map(r => r.T)) - 5, Tmx = Math.max(...rows.map(r => r.T)) + 5;
    const X = t => 50 + (W - 70) * t / t1, Y = T => 15 + (Hh - 45) * (1 - (T - Tmn) / (Tmx - Tmn)), step = Math.max(1, Math.floor(rows.length / 400));
    const pts = rows.filter((_, i) => i % step === 0).map(r => `<circle cx="${X(r.t).toFixed(1)}" cy="${Y(r.T).toFixed(1)}" r="1.6" fill="#8a8984"/>`).join("");
    const line = `<polyline fill="none" stroke="#c2410c" stroke-width="2" points="${m.map((v, i) => X(rows[i].t).toFixed(1) + "," + Y(v).toFixed(1)).join(" ")}"/>`;
    let ax = ""; for (const T of [150, 200, 220, 230, 250]) if (T > Tmn && T < Tmx) ax += `<line x1="50" x2="${W - 20}" y1="${Y(T)}" y2="${Y(T)}" stroke="#eee"/><text x="44" y="${Y(T) + 4}" text-anchor="end" font-size="11" fill="#8a8984">${T}</text>`;
    $("pChart").innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${Hh}" font-family="Cairo" direction="ltr" style="margin-top:8px">${ax}${pts}${line}<text x="${W - 20}" y="${Hh - 8}" text-anchor="end" font-size="11" fill="#52514e">${fmt(t1 / 60, 1)} h</text><text x="60" y="${Hh - 8}" font-size="11" fill="#52514e">النقاط: القياس · الخط: النموذج بأفضل G</text></svg>`;
  }
  function demoCsv() {
    const rows = [{ t: 0, T: 255, Ta: 30 }]; for (let i = 1; i <= 1800; i++) rows.push({ t: i, T: 0, Ta: 30 + 4 * Math.sin(i / 1440 * 2 * Math.PI) });
    const m = simCool(0.40, rows), r2 = (seed => () => (seed = (seed * 16807) % 2147483647) / 2147483647)(11);
    $("pCsv").value = "time_min,T2,T6\n" + rows.map((r, i) => `${r.t},${(m[i] + (r2() - 0.5) * 0.8).toFixed(2)},${r.Ta.toFixed(1)}`).join("\n");
    $("pOut").className = "status"; $("pOut").textContent = "بيانات تجريبية مولَّدة بـ G = 0.40 W/K مع ضجيج قياس؛ اضغط «طابق منحنى التبريد» لترى أن المطابقة تستعيدها.";
  }
  function plateFlux() {
    const P = +$("fKg").value * 4.186 * +$("fDT").value / (+$("fMin").value * 60), A = Math.PI * (+$("fD").value / 100) ** 2 / 4, q = P / A;
    const v = q >= 5 ? ["good", "الصاج العادي يكفي لكسرة المنزل (تحتاج نحو 4.8 kW/m²)."] : q >= 4 ? ["mid", "حدّي: جرّب الصاج ذا الزعانف B."] : ["bad", "أقل من المطلوب: الزعانف أو صاج أكبر أو أنابيب حرارية في P2."];
    $("pOut").className = "status " + (v[0] === "bad" ? "err" : "ok");
    $("pOut").innerHTML = `القدرة الواصلة للقدر <b class="lt">${fmt(P * 1000)} W</b> على مساحة <b class="lt">${fmt(A, 4)} m²</b> = <b class="lt">${fmt(q, 2)} kW/m²</b>. <span class="${v[0]}">${v[1]}</span>`;
  }
  function applyMeas() {
    if (!meas) return;
    GE.INSUL.meas = { ar: `مقاس من P1: k=${meas.k.toFixed(3)}، 200 مم`, k: meas.k, t: 0.20, rho: 120, usdM3: 180 };
    GE.INSUL.measC = { ar: `مقاس من P1: k=${meas.k.toFixed(3)}، 250 مم`, k: meas.k, t: 0.25, rho: 120, usdM3: 180 };
    $("insul").innerHTML = Object.keys(GE.INSUL).map(k => `<option value="${k}">${GE.INSUL[k].ar}</option>`).join("");
    $("insul").value = isCentral() ? "measC" : "meas"; showVals(); run(); renderSizes();
    $("pOut").innerHTML += "<br>طُبِّق: اختر «أصغر عدد وحدات يكفي» أو احسب المصفوفات من جديد لترى أثره.";
  }
  $("btnHold").onclick = holdTest; $("btnFit").onclick = fitCool; $("btnDemo").onclick = demoCsv; $("btnFlux").onclick = plateFlux; $("btnApply").onclick = applyMeas;

  initControls(); run(); renderDrawing("module"); renderSizes();
})();
