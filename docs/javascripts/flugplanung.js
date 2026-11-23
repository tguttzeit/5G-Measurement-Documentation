// Flight planning calculator for the measurement interval (page "Konfiguration").
// Every field can be entered or left empty; the missing ones are derived from the
// entered ones through the relations below, as far as they determine them.
(function () {
  "use strict";

  var VARS = ["v", "t", "d", "b", "L", "W", "S", "T", "N"];

  // Each relation solves for any one of its variables once all others are known.
  var RELATIONS = [
    { // point spacing along a track = speed * interval
      vars: ["d", "v", "t"],
      solve: {
        d: function (x) { return x.v * x.t; },
        v: function (x) { return x.d / x.t; },
        t: function (x) { return x.d / x.v; },
      },
      check: function (x) { return [x.d, x.v * x.t]; },
    },
    { // track length = speed * flight time
      vars: ["S", "v", "T"],
      solve: {
        S: function (x) { return x.v * x.T; },
        v: function (x) { return x.S / x.T; },
        T: function (x) { return x.S / x.v; },
      },
      check: function (x) { return [x.S, x.v * x.T]; },
    },
    { // number of points = track length / point spacing
      vars: ["N", "S", "d"],
      solve: {
        N: function (x) { return x.S / x.d; },
        S: function (x) { return x.N * x.d; },
        d: function (x) { return x.S / x.N; },
      },
      check: function (x) { return [x.N, x.S / x.d]; },
    },
    { // meander over a rectangle of L x W: W / b + 1 tracks of length L along L, plus the
      // connecting legs across, which add up to W
      vars: ["S", "L", "W", "b"],
      solve: {
        S: function (x) { return x.L * (x.W / x.b + 1) + x.W; },
        L: function (x) { return (x.S - x.W) / (x.W / x.b + 1); },
        W: function (x) { return (x.S - x.L) / (x.L / x.b + 1); },
        b: function (x) { return x.W / ((x.S - x.W) / x.L - 1); },
      },
      check: function (x) { return [x.S, x.L * (x.W / x.b + 1) + x.W]; },
    },
  ];
  var SQUARE = {
    vars: ["d", "b"],
    solve: { d: function (x) { return x.b; }, b: function (x) { return x.d; } },
    check: function (x) { return [x.d, x.b]; },
  };

  function solve(known, square) {
    var x = Object.assign({}, known);
    var relations = square ? RELATIONS.concat([SQUARE]) : RELATIONS;
    var changed = true;
    while (changed) {
      changed = false;
      relations.forEach(function (r) {
        var missing = r.vars.filter(function (k) { return x[k] === undefined; });
        if (missing.length !== 1) return;
        var value = r.solve[missing[0]](x);
        if (isFinite(value) && value > 0) {
          x[missing[0]] = value;
          changed = true;
        }
      });
    }
    var conflict = relations.some(function (r) {
      if (!r.vars.every(function (k) { return x[k] !== undefined; })) return false;
      var pair = r.check(x);
      return Math.abs(pair[0] - pair[1]) > 0.01 * Math.max(Math.abs(pair[0]), Math.abs(pair[1]));
    });
    return { values: x, conflict: conflict };
  }

  function format(value, lang) {
    var digits = value >= 100 ? 0 : value >= 10 ? 1 : 2;
    return value.toLocaleString(lang, { maximumFractionDigits: digits, useGrouping: false });
  }

  // A field may show its value in another unit than the solver uses (data-scale, e.g. minutes
  // for a flight time the solver keeps in seconds).
  function scale(input) { return Number(input.dataset.scale || 1); }

  function parse(input) {
    var raw = input.value.trim().replace(",", ".");
    if (raw === "") return undefined;
    var value = Number(raw);
    return isFinite(value) && value > 0 ? value * scale(input) : NaN;
  }

  function setup(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = "1";
    var lang = document.documentElement.lang || "de";
    var fields = {};
    VARS.forEach(function (k) { fields[k] = root.querySelector('[data-var="' + k + '"]'); });
    var square = root.querySelector("[data-square]");
    var out = function (name) { return root.querySelector('[data-out="' + name + '"]'); };

    function update() {
      var known = {}, invalid = false;
      VARS.forEach(function (k) {
        var f = fields[k];
        if (!f) return;
        if (f.dataset.derived === "1") { f.value = ""; f.dataset.derived = ""; }
        var value = parse(f);
        if (Number.isNaN(value)) { invalid = true; return; }
        if (value !== undefined) known[k] = value;
      });
      var result = solve(known, square && square.checked);
      VARS.forEach(function (k) {
        var f = fields[k];
        if (!f || known[k] !== undefined) return;
        if (result.values[k] !== undefined) {
          f.value = format(result.values[k] / scale(f), lang);
          f.dataset.derived = "1";
        }
      });
      var x = result.values;
      out("kmh").textContent = x.v !== undefined ? format(x.v * 3.6, lang) : "–";
      out("tracks").textContent = x.W !== undefined && x.b !== undefined
        ? String(Math.floor(x.W / x.b + 1e-9) + 1) : "–";
      out("interval").textContent = x.t !== undefined ? format(x.t, lang) : "–";
      out("threshold").textContent = x.d !== undefined ? format(x.d, lang) : "–";

      var notes = [];
      if (invalid) notes.push(root.dataset.msgInvalid);
      if (result.conflict) notes.push(root.dataset.msgConflict);
      if (x.t !== undefined && x.t < 1) notes.push(root.dataset.msgShortInterval);
      if (x.d !== undefined && x.d < 10) notes.push(root.dataset.msgShortDistance);
      var box = out("notes");
      box.innerHTML = "";
      notes.forEach(function (n) {
        var p = document.createElement("p");
        p.textContent = n;
        box.appendChild(p);
      });
      box.hidden = notes.length === 0;
    }

    VARS.forEach(function (k) {
      var f = fields[k];
      if (!f) return;
      f.addEventListener("input", function () { f.dataset.derived = ""; update(); });
    });
    if (square) square.addEventListener("change", update);
    var reset = root.querySelector("[data-reset]");
    if (reset) reset.addEventListener("click", function () {
      VARS.forEach(function (k) { if (fields[k]) { fields[k].value = ""; fields[k].dataset.derived = ""; } });
      update();
    });
    update();
  }

  function init() { document.querySelectorAll(".flugplanung").forEach(setup); }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
