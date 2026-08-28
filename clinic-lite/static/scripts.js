// ClinicCare-Lite - minimal progressive enhancement (no framework).

// 1. Auto-refresh an open conversation every 12s (periodic polling, per brief).
(function () {
  const chat = document.querySelector("[data-poll-conversation]");
  if (!chat) return;
  setInterval(() => {
    fetch(window.location.href, { headers: { "X-Requested-With": "poll" } })
      .then((r) => r.text())
      .then((html) => {
        const doc = new DOMParser().parseFromString(html, "text/html");
        const fresh = doc.querySelector("[data-poll-conversation]");
        if (fresh && fresh.innerHTML !== chat.innerHTML) {
          chat.innerHTML = fresh.innerHTML;
          chat.scrollTop = chat.scrollHeight;
        }
      })
      .catch(() => {});
  }, 12000);
  chat.scrollTop = chat.scrollHeight;
})();

// 2. Client-side ID + password hints on the register form (server still validates).
(function () {
  const form = document.querySelector("form[data-validate-register]");
  if (!form) return;
  const id = form.querySelector("[name=user_id]");
  const role = form.querySelector("[name=role]");
  const hint = form.querySelector("[data-id-hint]");
  function update() {
    if (!hint) return;
    const v = id.value.trim();
    if (!/^\d{8}$/.test(v)) { hint.textContent = "ID must be exactly 8 digits."; return; }
    if (role.value === "clinician" && !v.endsWith("0000")) {
      hint.textContent = "Clinician IDs must end in 0000."; return;
    }
    if (role.value === "patient") {
      const y = parseInt(v.slice(-4), 10);
      if (y < 2022 || y > 2028) { hint.textContent = "Patient IDs must end in a year 2022-2028."; return; }
    }
    hint.textContent = "Looks valid.";
  }
  id.addEventListener("input", update);
  role.addEventListener("change", update);
})();

// 3. Confirm destructive actions.
document.querySelectorAll("[data-confirm]").forEach((el) => {
  el.addEventListener("submit", (e) => {
    if (!confirm(el.getAttribute("data-confirm"))) e.preventDefault();
  });
});
