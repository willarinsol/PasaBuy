const $ = (id) => document.getElementById(id);

const profile = {
  name: "",
  photo: "",
  initials: "IB",
  role: "Student",
  studentId: "1040-25",
  program: "BS Criminology",
  email: "ianpogi@example.com",
  phone: "09XX XXX XXXX",
};

const rating = {
  score: 4.95,
  orders: 142,
  positive: 98,
  trust: "TOP TIER TRUST",
  criteria: [
    { label: "Food Temp & Freshness", value: 4.98, icon: "temp" },
    { label: "Punctuality & Speed", value: 4.92, icon: "clock" },
    { label: "Communication & Receipt Accuracy", value: 5.0, icon: "list" },
    { label: "Packaging & Zero-Spill Care", value: 4.96, icon: "shield" },
  ],
};

const icons = {
  temp:  '<path d="M14 14.8V5a2 2 0 0 0-4 0v9.8a4 4 0 1 0 4 0z"/>',
  clock: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M10 2h4"/>',
  list:  '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M7 9h10M7 12h10M7 15h10"/>',
  shield:'<path d="M12 2 4 5v6c0 5 3.4 9.3 8 11 4.6-1.7 8-6 8-11V5z"/>',
};

function starSVG(fill, size) {
  const id = "g" + Math.random().toString(36).slice(2, 8);
  const dim = size ? ` width="${size}" height="${size}"` : "";
  return `<svg class="star"${dim} viewBox="0 0 24 24">
    <defs><linearGradient id="${id}"><stop offset="${fill * 100}%" stop-color="#f5a524"/><stop offset="${fill * 100}%" stop-color="#d9dde5"/></linearGradient></defs>
    <path fill="url(#${id})" d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>`;
}

function renderProfile(p) {
  $("fullName").textContent = p.name;
  $("role").textContent = p.role;
  $("studentId").textContent = p.studentId;
  $("program").textContent = p.program;
  $("email").textContent = p.email;
  $("phone").textContent = p.phone;
  $("initials").textContent = p.initials;

  const img = $("avatarImg");
  if (p.photo) { img.src = p.photo; img.hidden = false; }
  else { img.removeAttribute("src"); img.hidden = true; }

  const first = p.name ? p.name.split(",").pop().trim().split(" ")[0] : "";
  $("pasabuyLabel").textContent = first ? `PasaBuy Food from ${first}` : "PasaBuy Food";
}

function renderRating(r) {
  $("score").textContent = r.score.toFixed(2);
  $("based").textContent = `Based on ${r.orders} Verified Orders`;
  $("positive").textContent = `${r.positive}% Positive Peer Feedback`;
  $("trust").textContent = r.trust;
  $("stars").innerHTML = [0, 1, 2, 3, 4]
    .map((i) => starSVG(Math.max(0, Math.min(1, r.score - i))))
    .join("");

  $("criteria").innerHTML = r.criteria.map((c) => `
    <li>
      <div class="crit-top">
        <span class="crit-name"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${icons[c.icon]}</svg>${c.label}</span>
        <span class="crit-score">${c.value.toFixed(c.value === 5 ? 1 : 2)} ${starSVG(1, 14)}</span>
      </div>
      <div class="bar" role="img" aria-label="${c.label} ${c.value} out of 5"><i data-w="${(c.value / 5) * 100}"></i></div>
    </li>`).join("");

  requestAnimationFrame(() => requestAnimationFrame(() => {
    document.querySelectorAll(".bar > i").forEach((el) => (el.style.width = el.dataset.w + "%"));
  }));
}

$("pasabuy").addEventListener("click", () => console.log("PasaBuy clicked"));
$("message").addEventListener("click", () => console.log("Send Message clicked"));

renderProfile(profile);
renderRating(rating);