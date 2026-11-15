(function () {
  var root = document.documentElement;
  var startedAt = Date.now();
  var loading = false;
  var initialReady = false;
  var initialTimer;

  root.classList.add("page-loading");

  function rectOf(element) {
    var rect = element.getBoundingClientRect();
    return {
      left: rect.left + window.pageXOffset,
      top: rect.top + window.pageYOffset,
      width: rect.width,
      height: rect.height
    };
  }

  function addShape(layer, rect, type, radius) {
    if (rect.width < 2 || rect.height < 2) { return; }
    var shape = document.createElement("span");
    shape.className = "page-skeleton__shape page-skeleton__shape--" + type;
    shape.style.left = rect.left + "px";
    shape.style.top = rect.top + "px";
    shape.style.width = rect.width + "px";
    shape.style.height = rect.height + "px";
    var corners = (radius || "").split(/\s+/);
    if (type === "text") {
      shape.style.borderRadius = "999px";
    } else if (corners.some(function (corner) { return corner.indexOf("%") !== -1; })) {
      shape.style.borderRadius = radius;
    } else {
      shape.style.borderRadius = corners.map(function (corner) {
        return parseFloat(corner) > 0 ? corner : "8px";
      }).join(" ");
    }
    layer.appendChild(shape);
  }

  function buildSkeleton() {
    var layer = document.getElementById("page-skeleton");
    if (!layer || !document.body) { return false; }

    layer.textContent = "";
    layer.style.height = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight,
      window.innerHeight
    ) + "px";

    document.body.querySelectorAll(".masthead, footer, .panel, .item, .card, .table-responsive, table, .consent-check, .tabbar, .d-head").forEach(function (element) {
      if (document.body.classList.contains("auth") && element.closest(".auth-wrap")) { return; }
      var rect = rectOf(element);
      var style = window.getComputedStyle(element);
      if (rect.width < 2 || rect.height < 2 || style.display === "none") { return; }
      var type = element.matches(".masthead, .d-head") ? "brand" : element.matches("footer") ? "footer" : "surface";
      addShape(layer, rect, type, style.borderRadius);
    });

    document.body.querySelectorAll("img, input:not([type=hidden]), select, textarea, button, .avatar, .story .ring, .ig-av, .thumb, .news-cover, .doc-ico, svg.i").forEach(function (element) {
      if (element.closest("#page-skeleton")) { return; }
      var rect = rectOf(element);
      var style = window.getComputedStyle(element);
      if (rect.width < 2 || rect.height < 2 || style.display === "none") { return; }
      addShape(layer, rect, "media", style.borderRadius);
    });

    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      if (!node.nodeValue.trim()) { continue; }
      var parent = node.parentElement;
      if (!parent || parent.closest("#page-skeleton,script,style,template,[aria-hidden='true']")) { continue; }
      var range = document.createRange();
      range.selectNodeContents(node);
      Array.prototype.forEach.call(range.getClientRects(), function (rect) {
        if (rect.width < 2 || rect.height < 2) { return; }
        var height = Math.max(4, Math.min(10, rect.height * 0.52));
        addShape(layer, {
          left: rect.left + window.pageXOffset,
          top: rect.top + window.pageYOffset + (rect.height - height) / 2,
          width: rect.width,
          height: height
        }, "text", height + "px");
      });
    }

    return true;
  }

  function hideSkeleton() {
    if (!loading) { return; }
    root.classList.remove("page-loading");
    var layer = document.getElementById("page-skeleton");
    if (layer) { layer.textContent = ""; layer.style.height = ""; }
    loading = false;
  }

  function finishInitialLoad() {
    if (initialReady) { return; }
    initialReady = true;
    window.clearTimeout(initialTimer);
    window.setTimeout(hideSkeleton, Math.max(0, 320 - (Date.now() - startedAt)));
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!buildSkeleton()) {
      root.classList.remove("page-loading");
      return;
    }
    loading = true;
  });

  window.addEventListener("load", finishInitialLoad);

  initialTimer = window.setTimeout(finishInitialLoad, 10000);
})();
