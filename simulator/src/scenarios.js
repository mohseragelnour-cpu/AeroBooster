/* AeroBooster revision C – scenario library. Loads are for the whole site; the engine divides them
   among N identical modules. kWh = heat taken from the salt store; floor = minimum store temperature. */
(function (root) {
  "use strict";
  const teaBoils = (from, to, every, litres, name) => {
    const a = []; for (let t = from; t <= to + 1e-9; t += every) a.push({ name: name || "tea", t: Math.round(t * 4) / 4, boilL: litres, floor: 150 });
    return a;
  };
  const HOUSE = (k) => ({
    fixed: [
      { name: "breakfast", t: 7, kwh: 0.35 * k, kw: 0.7 * k, floor: 150 },
      { name: "main", t: 13, kwh: 0.90 * k, kw: 1.0 * k, floor: 150 },
      { name: "evening", t: 19, kwh: 0.60 * k, kw: 0.8 * k, floor: 150 },
      ...[7.5, 11, 16.5, 21].map(t => ({ name: "tea", t, boilL: 1.5 * k, floor: 150 }))
    ],
    flex: [
      { name: "kisra", perWeek: 3, window: [10, 17], kwh: 0.73 * k, kw: 0.6 * k, floor: 215, start: 245, urgent: 222, exclusive: true },
      { name: "oven", perWeek: 2, window: [11, 15], kwh: 0.54 * k, kw: 0.55 * k, floor: 235, start: 248, urgent: 238, exclusive: true }
    ],
    water: [
      { name: "washing", t: 8, litres: 55 * k, temp: 45 }, { name: "washing", t: 18, litres: 55 * k, temp: 45 },
      { name: "hygiene", t: 15, litres: 12 * k, temp: 60 }
    ],
    heating: { months: [0, 1, 11], from: 20, to: 5, kw: 0.3 * k }
  });

  const SCENARIOS = [
    { id: "kiosk", icon: "kiosk", title: "كشك أو عربة شاي", en: "Tea kiosk / cart",
      who: "بائع شاي وقهوة من 07:00 إلى 22:00، نحو 180 كوبًا في اليوم، مع قلي خفيف عصرًا",
      fixed: [...teaBoils(7, 22, 0.5, 1.5, "tea"), { name: "frying", t: 16.5, kwh: 0.4, kw: 0.8, floor: 180 }],
      flex: [], water: [{ name: "dishwater", t: 12, litres: 20, temp: 45 }, { name: "dishwater", t: 21, litres: 20, temp: 45 }],
      heating: null,
      hw: { storeL: 30, pvM2: 5, troughM2: 0, flatM2: 1, tankL: 60, modules: 1, insul: "rw200" },
      note: "الماء يُسخَّن مسبقًا في خزان 60 لترًا، فيحتاج كل غلي إلى ثلث حرارة الماء البارد تقريبًا. الكشك يبيع أيضًا ماء شرب مبستر من فائض الحرارة." },
    { id: "small", icon: "smallhouse", title: "منزل صغير (2–4 أفراد)", en: "Small home",
      who: "ثلاث وجبات، الكسرة يومين والفرن يومًا في الأسبوع",
      ...(() => { const h = HOUSE(0.5); h.flex[0].perWeek = 2; h.flex[1].perWeek = 1; return h; })(),
      hw: { storeL: 30, pvM2: 4, troughM2: 0, flatM2: 1.5, tankL: 80, modules: 1, insul: "rw200" } },
    { id: "home", icon: "house", title: "منزل عادي (6–8 أفراد)", en: "Household (revision C)",
      who: "التصميم المرجعي للنسخة C: ثلاث وجبات، كسرة 3 أيام، فرن يومان، ماء ساخن وتدفئة شتوية",
      ...HOUSE(1),
      hw: { storeL: 45, pvM2: 6.5, troughM2: 0, flatM2: 2, tankL: 120, modules: 1, insul: "rw200" } },
    { id: "shared", icon: "shared", title: "منزل مشترك (15–20 فردًا)", en: "Shared home",
      who: "أسرتان أو ثلاث في مسكن واحد؛ الأحمال 2.5 ضعف المنزل العادي",
      ...(() => { const h = HOUSE(2.5); h.flex[0].perWeek = 4; return h; })(),
      hw: { storeL: 45, pvM2: 6, troughM2: 0, flatM2: 2, tankL: 120, modules: 3, insul: "rw200" } },
    { id: "communal", icon: "communal", title: "مطبخ جماعي (نحو 200 شخص)", en: "Communal kitchen",
      who: "مطبخ مخيم أو حي: ثلاث وجبات، كسرة يومية، فرن 3 أيام، شاي كل ساعة",
      fixed: [
        { name: "breakfast", t: 7, kwh: 10, kw: 10, floor: 150 },
        { name: "main", t: 12.5, kwh: 26, kw: 13, floor: 150 },
        { name: "evening", t: 18.5, kwh: 17, kw: 12, floor: 150 },
        ...teaBoils(7, 21, 1, 10, "tea")
      ],
      flex: [
        { name: "kisra", perWeek: 7, window: [10, 17], kwh: 14, kw: 7, floor: 215, start: 240, urgent: 222, exclusive: true },
        { name: "oven", perWeek: 3, window: [11, 15], kwh: 8, kw: 6, floor: 235, start: 248, urgent: 238, exclusive: true }
      ],
      water: [{ name: "washing", t: 8, litres: 400, temp: 45 }, { name: "washing", t: 15, litres: 400, temp: 45 }, { name: "hygiene", t: 15, litres: 100, temp: 60 }],
      heating: null,
      hw: { storeL: 45, pvM2: 9, troughM2: 0, flatM2: 2, tankL: 120, modules: 23, insul: "rw200" },
      plant: { insul: "rw250", storeL: 600, pvM2: 110, flatM2: 16, tankL: 1500, stations: 6, maxOutKw: 20, loopLossKw: 0.5, loopDT: 20, cartsPerDay: 10, pipeM: 30 } },
    { id: "cafeteria", icon: "cafe", title: "كافتيريا (نحو 150 وجبة)", en: "Cafeteria",
      who: "فطور وغداء، شاي وقهوة كل نصف ساعة من 08:00 إلى 20:00، قلي عصرًا، فرن 5 أيام",
      fixed: [
        { name: "breakfast", t: 8, kwh: 4, kw: 4, floor: 150 },
        { name: "main", t: 12, kwh: 18, kw: 9, floor: 150 },
        { name: "frying", t: 16, kwh: 3, kw: 3, floor: 180 },
        ...teaBoils(8, 20, 0.5, 3, "tea")
      ],
      flex: [{ name: "oven", perWeek: 5, window: [10, 15], kwh: 4, kw: 3, floor: 235, start: 246, urgent: 238, exclusive: true }],
      water: [{ name: "dishwater", t: 10, litres: 100, temp: 45 }, { name: "dishwater", t: 14, litres: 100, temp: 45 }, { name: "dishwater", t: 20, litres: 100, temp: 45 }],
      heating: null,
      hw: { storeL: 45, pvM2: 9, troughM2: 0, flatM2: 2, tankL: 120, modules: 12, insul: "rw200" },
      plant: { insul: "rw250", storeL: 400, pvM2: 55, flatM2: 8, tankL: 800, stations: 4, maxOutKw: 14, loopLossKw: 0.3, loopDT: 20, cartsPerDay: 6, pipeM: 20 } },
    { id: "bakery", icon: "bakery", title: "مخبز تجاري (كسرة وخبز)", en: "Commercial bakery",
      who: "إنتاج يومي في الظهيرة والعصر: نحو 12 كيلوواط ساعة كسرة و8 للفرن، 7 أيام",
      fixed: [{ name: "staff meal", t: 13, kwh: 1, kw: 1, floor: 150 }],
      flex: [
        { name: "kisra", perWeek: 7, window: [10, 17], kwh: 12, kw: 6, floor: 215, start: 240, urgent: 222, exclusive: true },
        { name: "oven", perWeek: 7, window: [10, 16], kwh: 8, kw: 5, floor: 235, start: 246, urgent: 236, exclusive: true }
      ],
      water: [{ name: "washing", t: 18, litres: 150, temp: 45 }],
      heating: null,
      hw: { storeL: 45, pvM2: 9, troughM2: 0, flatM2: 2, tankL: 120, modules: 20, insul: "rw200" },
      plant: { insul: "rw250", storeL: 1000, pvM2: 73, flatM2: 6, tankL: 600, stations: 4, maxOutKw: 14, loopLossKw: 0.3, loopDT: 20, cartsPerDay: 6, pipeM: 15 },
      note: "الخبز يُجدول بعد الظهر حين يمتلئ المخزن؛ الخبز الصباحي الباكر يحتاج مخزنًا أكبر بكثير." },
    { id: "factory", icon: "factory", title: "مصنع أغذية صغير", en: "Food factory (process heat)",
      who: "حرارة عملية 3 كيلوواط من 09:00 إلى 16:00 عند 180 °م أو أكثر: تحميص السمسم والفول، تجفيف، بسترة",
      fixed: [
        ...[9, 10, 11, 12, 13, 14, 15].map(t => ({ name: "process", t, kwh: 3, kw: 3, floor: 180 })),
        { name: "staff meal", t: 13, kwh: 1.5, kw: 1.5, floor: 150 }
      ],
      flex: [],
      water: [{ name: "cleaning", t: 16.5, litres: 300, temp: 45 }],
      heating: null,
      hw: { storeL: 45, pvM2: 7.5, troughM2: 0, flatM2: 2, tankL: 120, modules: 5, insul: "rw200" },
      note: "حرارة النهار تأتي من الألواح مباشرة تقريبًا؛ المخزن يغطي الغيوم والساعات الأولى." }
  ];
  if (typeof module !== "undefined" && module.exports) module.exports = SCENARIOS; else root.AB_SCENARIOS = SCENARIOS;
})(typeof window !== "undefined" ? window : globalThis);
