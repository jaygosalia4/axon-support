// The Axon sign-in page. It holds no secret of its own and stores nothing: it reads the
// sign-in handle from the URL FRAGMENT (no server ever receives a fragment), asks Axon's
// server who is signing in, then either hands the handle to the Axon app ("Open Axon": the
// person taps Allow there, and this page asks every few seconds until it is approved) or
// sends a typed one-time code — and follows the answer back to the assistant. Only this page,
// never the app, receives the code that finishes the sign-in. No cookies, no storage, no
// analytics, no third-party script.
(function () {
  "use strict";
  var API = "https://qnpnvdainbakygnnktrn.supabase.co/functions/v1/ai";

  // Never inside a frame: a framing page could watch what is typed or trick the click.
  if (window.top !== window.self) {
    document.documentElement.innerHTML = "";
    return;
  }

  function $(id) { return document.getElementById(id); }
  // "Open Axon" works where the app lives: an iPhone or iPad (iPadOS reports a Mac with touch).
  var onIOS = /iPhone|iPad|iPod/.test(navigator.userAgent)
    || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  function show(id) {
    ["loading", "start", "form", "done", "ended"].forEach(function (s) { $(s).hidden = s !== id; });
  }
  function post(path, body) {
    return fetch(API + path, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      credentials: "omit",
      referrerPolicy: "no-referrer",
      cache: "no-store",
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, body: j }; });
    });
  }
  // The server checked the return address when the sign-in began; check again before leaving.
  function safeBack(u) {
    try {
      var url = new URL(u);
      if (url.protocol === "https:") return url.href;
      if (url.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].indexOf(url.hostname) >= 0) return url.href;
    } catch (e) { /* not a URL */ }
    return null;
  }

  var handle = new URLSearchParams(window.location.hash.slice(1)).get("r");
  // Take the handle out of the address bar and the history at once.
  if (window.location.hash) history.replaceState(null, "", window.location.pathname);
  if (!handle || !/^[A-Za-z0-9_-]{43}$/.test(handle)) {
    show("start");
    return;
  }

  post("/oauth/request", { request: handle }).then(function (r) {
    if (r.status !== 200) {
      if (r.body && r.body.message) $("ended-text").textContent = r.body.message;
      show("ended");
      return;
    }
    var b = r.body;
    // Unverified = a program that registered itself (always on this computer: loopback only).
    $("who").textContent = b.verified ? b.client
      : b.client ? "A program on this computer that calls itself “" + b.client + "”"
      : "A program on this computer";
    $("what").textContent = (b.scopes || []).indexOf("write") >= 0
      ? "wants to read your Axon scores and daily summaries, and log mood check-ins, meals and naps for you while logging is on in Axon."
      : "wants to read your Axon scores and daily summaries.";
    $("where").textContent = b.return_to;
    $("back-to").textContent = b.verified ? b.client : "the program";
    $("unverified").hidden = !!b.verified;
    $("own").hidden = !b.verified;
    deadline = Date.now() + Math.max(0, b.expires_in || 0) * 1000;
    $("open-axon").href = "vitalscore://sign-in?r=" + encodeURIComponent(handle);
    $("app-way").hidden = !onIOS;
    $("code-way").open = !onIOS;
    show("form");
    if (!onIOS) $("code").focus();
  }, function () {
    $("ended-text").textContent = "Axon couldn't be reached. Check your connection, then start again from your assistant.";
    show("ended");
  });

  function leave(back) {
    polling = false;
    show("done");
    window.location.replace(back);
  }
  function end(msg) {
    polling = false;
    $("ended-text").textContent = msg || "This sign-in has expired or was already used. Start again from your assistant.";
    show("ended");
  }

  // ── Open Axon: the app approves; this page asks until it has been (free while waiting) ──
  var deadline = 0;
  var polling = false;
  var timer = null;
  var misses = 0;
  function poll() {
    clearTimeout(timer);
    if (!polling) return;
    if (Date.now() > deadline) { end(); return; }
    post("/oauth/approve", { request: handle, via: "app" }).then(function (r) {
      if (!polling) return;
      misses = 0;
      var back = r.status === 200 && r.body && safeBack(r.body.redirect);
      if (back) { leave(back); return; }
      if (r.status === 202) { timer = setTimeout(poll, 2000); return; }
      end(r.body && r.body.message);
    }, function () {
      // Offline for a moment (switching apps): keep asking, a little slower, then say so.
      misses += 1;
      if (misses >= 10) {
        polling = false;
        $("app-error").textContent = "Axon couldn't be reached. Check your connection, then tap Open Axon again.";
        $("app-error").hidden = false;
        return;
      }
      timer = setTimeout(poll, 4000);
    });
  }
  $("open-axon").addEventListener("click", function () {
    // The link itself opens the app; this page starts asking at once.
    $("waiting").hidden = false;
    $("app-error").hidden = true;
    misses = 0;
    if (!polling) { polling = true; timer = setTimeout(poll, 1500); }
  });
  // Back from Axon: ask straight away rather than at the next tick.
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible" && polling) poll();
  });

  $("code-form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var code = $("code").value.trim();
    var err = $("error");
    err.hidden = true;
    if (!code) {
      err.textContent = "Type the code Axon shows you.";
      err.hidden = false;
      return;
    }
    $("go").disabled = true;
    post("/oauth/approve", { request: handle, code: code }).then(function (r) {
      var back = r.status === 200 && r.body && safeBack(r.body.redirect);
      if (back) {
        leave(back);
        return;
      }
      var msg = (r.body && r.body.message) || "That didn't work. Start again from your assistant.";
      var error = r.body && r.body.error;
      if (error === "wrong_code") {
        err.textContent = msg;
        err.hidden = false;
        $("go").disabled = false;
        $("code").select();
        return;
      }
      end(msg);
    }, function () {
      err.textContent = "Axon couldn't be reached. Check your connection and try again.";
      err.hidden = false;
      $("go").disabled = false;
    });
  });
})();
