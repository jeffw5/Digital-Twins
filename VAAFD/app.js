(function () {
  "use strict";

  /* ---------- Logo concepts (original sketches) ---------- */
  function rays(cx, cy, r1, r2, angles, color, w) {
    return angles.map(function (a) {
      var t = (a * Math.PI) / 180;
      var x1 = cx + r1 * Math.cos(t), y1 = cy - r1 * Math.sin(t);
      var x2 = cx + r2 * Math.cos(t), y2 = cy - r2 * Math.sin(t);
      return '<line x1="' + x1.toFixed(1) + '" y1="' + y1.toFixed(1) + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '" stroke="' + color + '" stroke-width="' + w + '" stroke-linecap="round"/>';
    }).join("");
  }
  var LOGOS = {
    A: '<svg viewBox="0 0 64 64" role="img" aria-label="VAAFD logo, concept A: open eye with sun">' +
      '<circle cx="32" cy="32" r="31" fill="#0E4D3C"/>' +
      rays(32, 40, 25, 31, [90, 60, 120, 32, 148], "#F2A900", 3) +
      '<path d="M8 38 Q32 17 56 38 Q32 59 8 38Z" fill="#FBF6EC"/>' +
      '<circle cx="32" cy="38" r="10.500" fill="#F2A900"/><circle cx="32" cy="38" r="4.600" fill="#0E4D3C"/><circle cx="35" cy="35" r="1.700" fill="#FBF6EC"/></svg>',
    B: '<svg viewBox="0 0 64 64" role="img" aria-label="VAAFD logo, concept B: sun rising from an open book">' +
      '<circle cx="32" cy="32" r="31" fill="#F2A900"/>' +
      rays(32, 42, 17, 24, [165, 135, 105, 75, 45, 15], "#B8472A", 3) +
      '<path d="M21 42 A11 11 0 0 1 43 42Z" fill="#B8472A"/>' +
      '<path d="M8 42 Q20 36 32 42 L32 55 Q20 49 8 55Z" fill="#0E4D3C"/>' +
      '<path d="M56 42 Q44 36 32 42 L32 55 Q44 49 56 55Z" fill="#0A3A2D"/>' +
      '<path d="M32 42 V55" stroke="#FBF6EC" stroke-width="1.600"/></svg>',
    C: '<svg viewBox="0 0 64 64" role="img" aria-label="VAAFD logo, concept C: monogram A with sun and leaf">' +
      '<circle cx="32" cy="32" r="31" fill="#0E4D3C"/>' +
      '<path d="M16 52 L32 18 L48 52" fill="none" stroke="#FBF6EC" stroke-width="6.500" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<circle cx="32" cy="41" r="6" fill="#F2A900"/>' +
      '<path d="M32 19 Q33 8 47 8 Q47 20 32 19Z" fill="#F2A900"/><path d="M32 19 Q37 14 43 11" stroke="#0E4D3C" stroke-width="1.400" fill="none" stroke-linecap="round"/></svg>'
  };
  var KEY = "vaafd-logo";
  function getChoice() { try { return localStorage.getItem(KEY) || "A"; } catch (e) { return "A"; } }
  function setChoice(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function applyLogo() {
    var c = getChoice();
    document.querySelectorAll("[data-logo]").forEach(function (el) { el.innerHTML = LOGOS[c]; });
    document.querySelectorAll("[data-logo-preview]").forEach(function (el) { el.innerHTML = LOGOS[el.getAttribute("data-logo-preview")]; });
    document.querySelectorAll("[data-pick]").forEach(function (b) {
      var on = b.getAttribute("data-pick") === c;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.textContent = on ? "Selected" : "Use this logo";
      var card = b.closest(".logo-card");
      if (card) card.classList.toggle("picked", on);
    });
  }
  applyLogo();
  document.querySelectorAll("[data-pick]").forEach(function (b) {
    b.addEventListener("click", function () { setChoice(b.getAttribute("data-pick")); applyLogo(); });
  });

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.querySelector("[data-menu]");
  var nav = document.getElementById("nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Tabs ---------- */
  document.querySelectorAll("[data-tabs]").forEach(function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var p = document.getElementById(t.getAttribute("aria-controls"));
        if (p) p.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") n = tabs[0];
        if (e.key === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    var h = (location.hash || "").replace("#", "");
    if (h) {
      var target = root.querySelector('[id="' + h + '"]');
      var panel = target && target.closest('[role="tabpanel"]');
      if (panel) { var tab = root.querySelector('[aria-controls="' + panel.id + '"]'); if (tab) select(tab); }
    }
  });

  /* ---------- Donate widget (mock) ---------- */
  var IMPACT = {
    25: "[Add: what $25 provides, from the real budget]",
    50: "[Add: what $50 provides]",
    100: "[Add: what $100 provides]",
    250: "[Add: what $250 provides]",
    500: "[Add: what $500 provides]"
  };
  document.querySelectorAll("[data-give]").forEach(function (w) {
    var freq = "once", amt = 100;
    var total = w.querySelector("[data-total]"), flab = w.querySelector("[data-freqlabel]"),
      impact = w.querySelector("[data-impact]"), msg = w.querySelector("[data-msg]"), custom = w.querySelector("[data-custom]");
    function render() {
      total.textContent = "$" + (amt || 0);
      flab.textContent = freq === "monthly" ? "per month" : "";
      impact.textContent = IMPACT[amt] || "Thank you. Every gift supports a child's education.";
      w.querySelectorAll("[data-freq]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-freq") === freq ? "true" : "false"); });
      w.querySelectorAll("[data-amt]").forEach(function (b) { b.setAttribute("aria-pressed", Number(b.getAttribute("data-amt")) === amt && !custom.value ? "true" : "false"); });
    }
    w.querySelectorAll("[data-freq]").forEach(function (b) { b.addEventListener("click", function () { freq = b.getAttribute("data-freq"); render(); }); });
    w.querySelectorAll("[data-amt]").forEach(function (b) { b.addEventListener("click", function () { amt = Number(b.getAttribute("data-amt")); custom.value = ""; render(); }); });
    custom.addEventListener("input", function () { var v = parseInt(custom.value, 10); amt = v > 0 ? v : 0; render(); });
    w.querySelector("[data-go]").addEventListener("click", function () {
      msg.textContent = amt > 0 ? "Mockup only: this would open secure checkout for $" + amt + (freq === "monthly" ? " monthly." : ".") : "Please choose an amount.";
    });
    render();
  });

  /* ---------- Progress bars ---------- */
  function fmt(n) { return "$" + Number(n).toLocaleString("en-US"); }
  document.querySelectorAll("[data-progress]").forEach(function (p) {
    var raised = Number(p.getAttribute("data-raised")), goal = Number(p.getAttribute("data-goal"));
    p.querySelector("[data-raised-label]").textContent = fmt(raised);
    p.querySelector("[data-goal-label]").textContent = fmt(goal);
    var fill = p.querySelector(".bar-fill");
    var pct = Math.min(100, Math.round((raised / goal) * 100));
    p.querySelector(".bar-track").setAttribute("role", "img");
    p.querySelector(".bar-track").setAttribute("aria-label", pct + " percent of goal");
    function go() { fill.style.width = pct + "%"; }
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { go(); io.disconnect(); } }, { threshold: 0.3 });
      io.observe(p);
    } else { go(); }
  });

  /* ---------- Filters ---------- */
  document.querySelectorAll("[data-filters]").forEach(function (g) {
    var scope = g.parentElement;
    g.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-f");
        g.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        scope.querySelectorAll("[data-cat]").forEach(function (r) {
          r.setAttribute("data-hidden", f === "all" || r.getAttribute("data-cat") === f ? "false" : "true");
        });
      });
    });
  });

  /* ---------- Mock forms ---------- */
  document.querySelectorAll("[data-form]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var m = f.querySelector(".form-msg");
      if (!f.checkValidity()) { m.textContent = "Please complete the required fields."; return; }
      m.textContent = "Mockup only: nothing was sent. In the live site this goes to [confirmed inbox].";
      f.reset();
    });
  });

  /* ---------- Stat count-up ---------- */
  document.querySelectorAll("[data-count]").forEach(function (el) {
    var end = Number(el.getAttribute("data-count"));
    if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var io = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      io.disconnect();
      var t0 = null;
      function step(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 1100); el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); }
      requestAnimationFrame(step);
    }, { threshold: 0.6 });
    io.observe(el);
  });

  /* v2 */
  /* ---------- Grouped menu ---------- */
  var subs = Array.prototype.slice.call(document.querySelectorAll("[data-sub]"));
  function closeSubs(except) {
    subs.forEach(function (b) {
      if (b === except) return;
      b.setAttribute("aria-expanded", "false");
      b.parentElement.classList.remove("open");
    });
  }
  subs.forEach(function (b) {
    b.addEventListener("click", function () {
      var open = !b.parentElement.classList.contains("open");
      closeSubs(b);
      b.parentElement.classList.toggle("open", open);
      b.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function (e) { if (!e.target.closest(".has-sub")) closeSubs(); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var openBtn = document.querySelector(".has-sub.open [data-sub]");
    closeSubs();
    if (openBtn) openBtn.focus();
  });

  /* ---------- Careers: Apply links prefill the role ---------- */
  var roleSel = document.querySelector("[data-role-select]");
  document.querySelectorAll("[data-role]").forEach(function (a) {
    a.addEventListener("click", function () {
      if (!roleSel) return;
      var want = a.getAttribute("data-role");
      Array.prototype.forEach.call(roleSel.options, function (o, i) { if (o.textContent === want) roleSel.selectedIndex = i; });
    });
  });

  /* ---------- Shop cart (mock, kept in the page only) ---------- */
  var cartEl = document.querySelector("[data-cart]");
  if (cartEl) {
    var cart = [];
    var list = cartEl.querySelector("[data-cart-list]"), empty = cartEl.querySelector("[data-cart-empty]"),
      totalEl = cartEl.querySelector("[data-cart-total]"), cmsg = cartEl.querySelector("[data-cart-msg]");
    var drawCart = function () {
      var n = 0, sum = 0;
      list.textContent = "";
      cart.forEach(function (it, i) {
        n += it.qty; sum += it.qty * it.price;
        var li = document.createElement("li"), left = document.createElement("span"), right = document.createElement("span"), rm = document.createElement("button");
        left.textContent = it.qty + " × " + it.name;
        right.textContent = "$" + it.qty * it.price;
        rm.type = "button"; rm.textContent = "Remove"; rm.setAttribute("aria-label", "Remove " + it.name);
        rm.addEventListener("click", function () { cart.splice(i, 1); cmsg.textContent = ""; drawCart(); });
        right.appendChild(rm); li.appendChild(left); li.appendChild(right); list.appendChild(li);
      });
      empty.hidden = cart.length > 0;
      totalEl.textContent = "$" + sum;
      document.querySelectorAll("[data-cart-count]").forEach(function (c) { c.textContent = n; });
    };
    document.querySelectorAll("[data-add]").forEach(function (b) {
      b.addEventListener("click", function () {
        var name = b.getAttribute("data-name"), price = Number(b.getAttribute("data-price"));
        var hit = cart.filter(function (it) { return it.name === name; })[0];
        if (hit) hit.qty += 1; else cart.push({ name: name, price: price, qty: 1 });
        cmsg.textContent = "";
        b.textContent = "Added";
        setTimeout(function () { b.textContent = "Add to cart"; }, 900);
        drawCart();
      });
    });
    cartEl.querySelector("[data-checkout]").addEventListener("click", function () {
      cmsg.textContent = cart.length ? "Mockup only: this would open secure checkout with [store provider]." : "Add an item first.";
    });
    cartEl.querySelector("[data-cart-clear]").addEventListener("click", function () { cart = []; cmsg.textContent = ""; drawCart(); });
    drawCart();
  }
})();
