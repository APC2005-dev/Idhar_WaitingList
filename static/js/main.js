// ============================================================
// idhar waitlist — interactions
// ============================================================

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- scroll reveal ---------- */
  const revealEls = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('in'), i * 60);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealEls.forEach(el => io.observe(el));

  /* ---------- seamless marquee (duplicate track content) ---------- */
  const track = document.getElementById('marqueeTrack');
  if (track) {
    track.innerHTML += track.innerHTML;
  }

  /* ---------- ambient ink-blot texture in hero ---------- */
  const blotfield = document.getElementById('heroBlots');
  if (blotfield) {
    const sizes = [60, 90, 40, 120, 70, 50, 100];
    sizes.forEach((s, i) => {
      const b = document.createElement('div');
      b.className = 'blot';
      b.style.width = s + 'px';
      b.style.height = s + 'px';
      b.style.top = (Math.random() * 90) + '%';
      b.style.left = (Math.random() * 95) + '%';
      blotfield.appendChild(b);
    });
  }

  /* ---------- live waitlist count ---------- */
  const heroCountLine = document.getElementById('heroCountLine');
  fetch('/api/count')
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (data && heroCountLine) {
        heroCountLine.textContent = `${data.count}+ people already idhar. Join them.`;
      }
    })
    .catch(() => { });

  /* ---------- waitlist form ---------- */
  const form = document.getElementById('waitlistForm');
  const submitBtn = document.getElementById('submitBtn');
  const successState = document.getElementById('successState');
  const successMsg = document.getElementById('successMsg');
  const successCount = document.getElementById('successCount');

  const fieldMap = {
    name: 'field-name',
    email: 'field-email',
    age_group: 'field-age',
    role: 'field-role',
  };

  function clearErrors() {
    Object.values(fieldMap).forEach(id => {
      document.getElementById(id).classList.remove('has-error');
    });
  }

  function showErrors(errors) {
    Object.keys(errors).forEach(key => {
      const id = fieldMap[key];
      if (id) document.getElementById(id).classList.add('has-error');
    });
    const firstKey = Object.keys(errors)[0];
    if (firstKey && fieldMap[firstKey]) {
      document.getElementById(fieldMap[firstKey]).scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function clientValidate(payload) {
    const errors = {};
    if (!payload.name || payload.name.trim().length < 2) errors.name = true;
    const emailOk = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(payload.email || '');
    if (!emailOk) errors.email = true;
    if (!payload.age_group) errors.age_group = true;
    if (!payload.role) errors.role = true;
    return errors;
  }

  form && form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();

    const roleEl = form.querySelector('input[name="role"]:checked');
    const payload = {
      name: document.getElementById('name').value.trim(),
      email: document.getElementById('email').value.trim(),
      age_group: document.getElementById('age_group').value,
      role: roleEl ? roleEl.value : '',
      message: document.getElementById('message').value.trim(),
    };

    const clientErrors = clientValidate(payload);
    if (Object.keys(clientErrors).length) {
      showErrors(clientErrors);
      return;
    }

    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
      const res = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (res.status === 400 && data.errors) {
        showErrors(data.errors);
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        return;
      }

      if (!res.ok || (!data.ok && !data.already_joined)) {
        const errorMsg = (data.errors && data.errors._server) || "Something went wrong saving your entry. Please try again.";
        alert(errorMsg);
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        return;
      }

      if (data.already_joined) {
        successMsg.textContent = data.message || "You're already on the list — we'll be in touch.";
        successCount.style.display = 'none';
      } else if (data.ok) {
        successMsg.textContent = "Thanks for joining — we'll write to you the moment there's something to see.";
        if (typeof data.count === 'number') {
          successCount.textContent = `You're #${data.count} on the list`;
          successCount.style.display = 'inline-block';
        }
      }

      form.style.display = 'none';
      successState.classList.add('show');

    } catch (err) {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      alert("Something went wrong — please try again in a moment.");
    }
  });

});
