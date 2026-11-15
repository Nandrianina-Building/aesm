/* Consentement cookies + Google Analytics (chargé UNIQUEMENT après acceptation). */
(function () {
  var script = document.currentScript, id = script && script.getAttribute("data-ga");
  if (!id || !/^G-[A-Z0-9]+$/i.test(id)) { return; }
  var KEY = "aesm_cookie_consent", banner = document.getElementById("cookieBanner");
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function loadGA() {
    if (window.__gaLoaded) { return; }
    window.__gaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", id, { anonymize_ip: true, allow_google_signals: false, cookie_flags: "SameSite=Lax;Secure" });
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    document.head.appendChild(s);
  }
  function show() { if (banner) { banner.hidden = false; } }
  function hide() { if (banner) { banner.hidden = true; } }
  var c = get();
  if (c === "granted") { loadGA(); } else if (c !== "denied") { show(); }
  document.querySelectorAll("[data-consent]").forEach(function (b) {
    b.addEventListener("click", function () {
      var v = b.getAttribute("data-consent"); set(v); hide();
      if (v === "granted") { loadGA(); } else { document.cookie.split(";").forEach(function (k) { var n = k.split("=")[0].trim(); if (n.indexOf("_ga") === 0) { document.cookie = n + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/"; } }); }
    });
  });
  document.querySelectorAll("[data-cookie-settings]").forEach(function (b) { b.addEventListener("click", show); });
})();
