/* TechStyle — main.js
   Minimal vanilla JS helpers.
   No framework needed — we're keeping it simple for now.
*/

// ── Cart count badge (live update via API) ──────────────────────────
async function refreshCartBadge() {
  try {
    const res = await fetch('/api/cart/count');
    const data = await res.json();
    const badges = document.querySelectorAll('.cart-count-badge');
    badges.forEach(b => {
      b.textContent = data.count;
      b.style.display = data.count > 0 ? 'inline' : 'none';
    });
  } catch (e) {
    // silently ignore — not critical
  }
}

// ── Auto-dismiss flash alerts after 4s ─────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 4000);
  });
});

// ── Confirm before removing items ──────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });
});

// ── Simple quantity +/- helpers (used on product detail page) ───────
function increment() {
  const el = document.getElementById('qty');
  if (el) el.value = Math.min(parseInt(el.value || 1) + 1, parseInt(el.max || 99));
}

function decrement() {
  const el = document.getElementById('qty');
  if (el) el.value = Math.max(parseInt(el.value || 1) - 1, 1);
}
