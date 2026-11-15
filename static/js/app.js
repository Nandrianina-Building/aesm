document.addEventListener("submit", function (e) {
  var msg = e.target.getAttribute("data-confirm");
  if (msg && !window.confirm(msg)) { e.preventDefault(); }
});

/* Marque le lien actif (navigation haute, menu mobile, onglets, menu gestion) */
(function () {
  var path = location.pathname;
  document.querySelectorAll("a[data-nav]").forEach(function (a) {
    var href = a.getAttribute("href").split("?")[0];
    var exact = a.getAttribute("data-nav") === "exact" || href === "/";
    var on = exact ? path === href : path === href || path.indexOf(href) === 0;
    if (on) { a.classList.add("active"); a.setAttribute("aria-current", "page"); }
  });
  var best = null;
  document.querySelectorAll(".side a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (path === href || (path.indexOf(href) === 0 && (!best || href.length > best.getAttribute("href").length))) { best = a; }
  });
  if (best) { best.classList.add("active"); }
})();

/* Messages pop-up (toasts) : visibles 3 secondes, puis disparaissent seuls (ou au clic sur la croix) */
(function () {
  var DURATION = 3000;
  var ICON = { success: "check", error: "alert", warning: "alert", info: "info" };
  function stack() {
    var s = document.querySelector(".toast-stack");
    if (!s) {
      s = document.createElement("div");
      s.className = "toast-stack"; s.setAttribute("aria-live", "polite"); s.setAttribute("aria-atomic", "true");
      document.body.appendChild(s);
    }
    return s;
  }
  function dismiss(t) {
    if (!t || t.classList.contains("leaving")) { return; }
    t.classList.add("leaving");
    setTimeout(function () { var s = t.parentNode; t.remove(); if (s && !s.children.length && s.dataset.dyn) { s.remove(); } }, 380);
  }
  function arm(t) {
    var timer, remaining = DURATION, started;
    function start() { started = Date.now(); timer = setTimeout(function () { dismiss(t); }, remaining); }
    function stop() { clearTimeout(timer); remaining -= Date.now() - started; }
    t.addEventListener("mouseenter", stop);
    t.addEventListener("mouseleave", start);
    var c = t.querySelector(".t-close");
    if (c) { c.addEventListener("click", function () { dismiss(t); }); }
    start();
  }
  window.aesmToast = function (msg, type) {
    type = type || "info";
    var s = stack(); if (!s.children.length) { s.dataset.dyn = "1"; }
    var t = document.createElement("div");
    t.className = "toast-x t-" + type; t.setAttribute("role", "status");
    t.innerHTML = '<span class="t-ico"><svg class="i"><use href="#i-' + (ICON[type] || "info") + '"/></svg></span><div class="t-msg"></div>' +
      '<button type="button" class="t-close" aria-label="Fermer"><svg class="i"><use href="#i-x"/></svg></button><span class="t-bar"></span>';
    t.querySelector(".t-msg").textContent = msg;
    s.appendChild(t); arm(t);
  };
  document.querySelectorAll(".toast-x").forEach(arm);
  document.querySelectorAll("[data-toast]").forEach(function (el) {
    var txt = el.textContent.trim(); if (txt) { window.aesmToast(txt, el.getAttribute("data-toast")); }
  });
})();

/* Partage : feuille de partage native, sinon copie du lien */
document.addEventListener("click", function (e) {
  var b = e.target.closest("[data-share]"); if (!b) { return; }
  var url = location.origin + b.getAttribute("data-url"), title = b.getAttribute("data-title") || document.title;
  if (navigator.share) { navigator.share({ title: title, url: url }).catch(function () {}); return; }
  var done = function () { window.aesmToast("Lien copié dans le presse-papiers", "success"); };
  if (navigator.clipboard) { navigator.clipboard.writeText(url).then(done, function () { window.prompt("Copiez ce lien :", url); }); }
  else { window.prompt("Copiez ce lien :", url); }
});

/* Compteur « 1/3 » des carrousels façon Instagram */
document.addEventListener("slid.bs.carousel", function (e) {
  var c = e.target.querySelector("[data-counter]");
  if (c) { c.textContent = (e.to + 1) + "/" + e.target.querySelectorAll(".carousel-item").length; }
});

/* Menu d'espace : centre l'onglet actif (sans faire défiler la page) + indicateurs de débordement */
(function () {
  var sc = document.querySelector(".sm-scroll"); if (!sc) { return; }
  var wrap = sc.parentNode, a = sc.querySelector("a.active");
  function upd() {
    wrap.classList.toggle("more-l", sc.scrollLeft > 6);
    wrap.classList.toggle("more-r", sc.scrollLeft + sc.clientWidth < sc.scrollWidth - 6);
  }
  if (a) { sc.scrollLeft = a.offsetLeft - (sc.clientWidth - a.offsetWidth) / 2; }
  sc.addEventListener("scroll", upd, { passive: true }); window.addEventListener("resize", upd); upd();
})();

/* Tableaux : étiquettes de colonnes (cartes empilées sur mobile) et couleurs de statut */
(function () {
  var TONES = [[/(confirm|actif|active|pay[ée]|valid|publi|accept|r[ée]solu|trait[ée]|termin|visible|à jour|en cours)/i, "ok"],
               [/(attente|v[ée]rif|traitement|programm|brouillon|ouvert|à traiter|impay)/i, "warn"],
               [/(refus|annul|rejet|expir|[ée]chou|[ée]chec|suspend|d[ée]sactiv|masqu|archiv|rembours)/i, "bad"]];
  function tone(txt) { for (var i = 0; i < TONES.length; i++) { if (TONES[i][0].test(txt)) { return TONES[i][1]; } } return ""; }
  document.querySelectorAll("table.table").forEach(function (t) {
    var heads = Array.prototype.map.call(t.querySelectorAll("thead th"), function (th) { return th.textContent.trim(); });
    t.querySelectorAll("tbody tr").forEach(function (tr) {
      Array.prototype.forEach.call(tr.children, function (td, i) {
        if (heads[i] !== undefined) { td.setAttribute("data-label", heads[i]); }
        if (/^(statut|état|etat)$/i.test(heads[i] || "") && td.children.length === 0 && td.textContent.trim()) {
          var sp = document.createElement("span"); sp.className = "badge-s"; sp.textContent = td.textContent.trim();
          td.textContent = ""; td.appendChild(sp);
        }
      });
    });
  });
  document.querySelectorAll(".badge-s").forEach(function (b) { var k = tone(b.textContent); if (k) { b.setAttribute("data-tone", k); } });
})();

/* Aperçu des images choisies (photo de profil, affiches, galeries) */
(function () {
  function bind(input) {
    input.addEventListener("change", function () {
      var files = Array.prototype.slice.call(input.files || []).filter(function (f) { return /^image\//.test(f.type); });
      if (input.id === "id_photo") {
        var av = document.querySelector(".avatar-edit .avatar");
        if (av && files[0]) { av.innerHTML = '<img alt="Aperçu">'; av.firstChild.src = URL.createObjectURL(files[0]); }
        return;
      }
      var box = input.closest("form").querySelector("[data-preview-target]"); if (!box) { return; }
      box.querySelectorAll("[data-for='" + input.name + "']").forEach(function (n) { n.remove(); });
      files.forEach(function (f) {
        var im = document.createElement("img"); im.src = URL.createObjectURL(f); im.alt = "Aperçu"; im.setAttribute("data-for", input.name); box.appendChild(im);
      });
      box.hidden = !box.children.length;
    });
  }
  document.querySelectorAll("input[type=file][data-preview], #id_photo").forEach(bind);
})();

/* Champ de commentaire qui s'agrandit avec le texte */
document.querySelectorAll(".ig-compose textarea").forEach(function (t) {
  t.addEventListener("input", function () { t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight, 120) + "px"; });
});

/* Formulaires : évite le double envoi (clic répété) et indique le traitement en cours */
document.addEventListener("submit", function (e) {
  if (e.defaultPrevented) { return; }
  var form = e.target;
  if (!form.matches || !form.matches("form[method=post]")) { return; }
  setTimeout(function () {
    form.querySelectorAll("button:not([type]), button[type=submit]").forEach(function (b) { b.classList.add("is-loading"); b.setAttribute("aria-disabled", "true"); });
  }, 0);
  setTimeout(function () { form.querySelectorAll(".is-loading").forEach(function (b) { b.classList.remove("is-loading"); b.removeAttribute("aria-disabled"); }); }, 8000);
});

/* Actualités : épingle et cadenas (bascule pour la gestion, explication pour les autres) avec message toast */
document.addEventListener("click", function (e) {
  var b = e.target.closest("[data-pub-toggle], [data-pub-info]"); if (!b) { return; }
  if (b.hasAttribute("data-pub-info")) { window.aesmToast(b.getAttribute("data-pub-info"), "info"); return; }
  if (b.disabled) { return; }
  b.disabled = true;
  fetch(b.getAttribute("data-url"), {
    method: "POST", credentials: "same-origin",
    headers: { "X-CSRFToken": b.getAttribute("data-csrf"), "X-Requested-With": "XMLHttpRequest" }
  }).then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.json(); }).then(function (d) {
    var on = b.getAttribute("data-kind") === "pin" ? d.pinned : d.locked;
    b.classList.toggle("on", on); b.classList.toggle("off", !on); b.setAttribute("aria-pressed", on ? "true" : "false");
    window.aesmToast(d.message, d.level || "success");
  }).catch(function () {
    window.aesmToast("Action impossible pour le moment. Rechargez la page puis réessayez.", "error");
  }).then(function () { b.disabled = false; });
});
