// The Friends invite page. It reads the invite code from the URL FRAGMENT (no server ever
// receives a fragment), points "Open Axon" at the app, and shows the code to type. It makes
// no network call and stores nothing: no cookies, no storage, no analytics, no outside script.
// The code alphabet mirrors FriendCode in the app and friend_new_code() on the server.
(function () {
  "use strict";

  // Never inside a frame: a framing page could dress the code up as something else.
  if (window.top !== window.self) {
    document.documentElement.innerHTML = "";
    return;
  }

  function $(id) { return document.getElementById(id); }

  var raw = decodeURIComponent(window.location.hash.slice(1) || "");
  var code = raw.toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (!/^[ABCDEFGHJKMNPQRSTUVWXYZ23456789]{6}$/.test(code)) {
    $("nocode").hidden = false;
    return;
  }

  $("open").setAttribute("href", "vitalscore://friend?c=" + code);
  // "K7MQ4R" → "K7M Q4R": two halves are easier to read out and type.
  $("code").textContent = code.slice(0, 3) + " " + code.slice(3);
  $("invite").hidden = false;
})();
