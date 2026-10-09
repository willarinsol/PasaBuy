const $ = (id) => document.getElementById(id);

const profileDataElement = document.getElementById('profile-data');
const ratingDataElement = document.getElementById('rating-data');
const profile = profileDataElement ? JSON.parse(profileDataElement.textContent) : {};
const rating = ratingDataElement ? JSON.parse(ratingDataElement.textContent) : {};

const icons = {
  temp:  '<path d="M14 14.8V5a2 2 0 0 0-4 0v9.8a4 4 0 1 0 4 0z"/>',
  clock: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M10 2h4"/>',
  list:  '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M7 9h10M7 12h10M7 15h10"/>',
  shield:'<path d="M12 2 4 5v6c0 5 3.4 9.3 8 11 4.6-1.7 8-6 8-11V5z"/>'
};

function starSVG(fill, size) {
  const id = "g" + Math.random().toString(36).slice(2, 8);
  const dim = size ? ` width="${size}" height="${size}"` : "";
  return `<svg class="star"${dim} viewBox="0 0 24 24">
    <defs><linearGradient id="${id}"><stop offset="${fill * 100}%" stop-color="#f5a524"/><stop offset="${fill * 100}%" stop-color="#d9dde5"/></linearGradient></defs>
    <path fill="url(#${id})" d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>`;
}

function renderProfile(p) {
  if($("fullName")) $("fullName").textContent = p.name;
  if($("role")) $("role").textContent = p.role;
  if($("studentId")) $("studentId").textContent = p.studentId;
  if($("program")) $("program").textContent = p.program;
  if($("email")) $("email").textContent = p.email;
  if($("phone")) $("phone").textContent = p.phone;
  if($("avatarInitials")) $("avatarInitials").textContent = p.initials;

  if($("avatarImg")) {
    if (p.photo) {
      $("avatarImg").src = p.photo;
      $("avatarImg").hidden = false;
    } else {
      $("avatarImg").removeAttribute("src");
      $("avatarImg").hidden = true;
    }
  }

  // Hide/Show Social Links dynamically
  if (p.facebook) {
    if($("fbContainer")) $("fbContainer").hidden = false;
    if($("facebookLink")) {
        $("facebookLink").href = p.facebook;
        $("facebookLink").textContent = p.facebook.replace("https://", "").replace("www.", "");
    }
  } else {
    if($("fbContainer")) $("fbContainer").hidden = true;
  }

  if (p.instagram) {
    if($("igContainer")) $("igContainer").hidden = false;
    if($("instagramLink")) {
        $("instagramLink").href = p.instagram;
        $("instagramLink").textContent = p.instagram.replace("https://", "").replace("www.", "");
    }
  } else {
    if($("igContainer")) $("igContainer").hidden = true;
  }

  // Handle owner permissions (showing 'edit' btn)
  if (p.is_self) {
    if($("editContactBtn")) $("editContactBtn").hidden = false;
  } else {
    if($("editContactBtn")) $("editContactBtn").hidden = true;
  }
}

function renderRating(r) {
  if(!r || Object.keys(r).length === 0) return;
  
  if($("score")) $("score").textContent = r.score.toFixed(2);
  if($("based")) $("based").textContent = `Based on ${r.orders} Verified Orders`;
  if($("positive")) $("positive").textContent = `${r.positive}% Positive Peer Feedback`;
  if($("trust")) $("trust").textContent = r.trust;
  
  if($("stars")) {
      $("stars").innerHTML = [0, 1, 2, 3, 4]
        .map((i) => starSVG(Math.max(0, Math.min(1, r.score - i))))
        .join("");
  }

  // Render recent reviews
  if($("recentReviews") && r.recent_reviews) {
      if (r.recent_reviews.length === 0) {
         $("recentReviews").innerHTML = "<p class='no-reviews'>No reviews yet.</p>";
      } else {
         $("recentReviews").innerHTML = r.recent_reviews.map((rev) => `
           <div class="user-review">
             <div class="ur-av">${rev.reviewer_initials}</div>
             <div class="ur-content">
               <div class="ur-head">
                 <strong>${rev.reviewer_name}</strong>
                 <span class="ur-date">${rev.date}</span>
               </div>
               <div class="ur-stars">
                 ${[0, 1, 2, 3, 4].map(i => starSVG(Math.max(0, Math.min(1, rev.rating - i)), 14)).join("")}
               </div>
               ${rev.review_text ? `<p class="ur-text">"${rev.review_text}"</p>` : ''}
             </div>
           </div>
         `).join("");
      }
  }
}

// Bind Edit Interactions
if ($("editContactBtn")) {
  $("editContactBtn").addEventListener("click", () => {
    $("inputEmail").value = profile.email || "";
    $("inputPhone").value = profile.phone === "Not provided" ? "" : (profile.phone || "");
    $("inputFb").value = profile.facebook || "";
    $("inputIg").value = profile.instagram || "";
    $("editPanel").hidden = false;
  });
}

if ($("cancelEditBtn")) {
  $("cancelEditBtn").addEventListener("click", () => {
    $("editPanel").hidden = true;
    $("editError").textContent = "";
  });
}

if ($("editContactForm")) {
  $("editContactForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    const payload = {
      email: $("inputEmail").value,
      phone: $("inputPhone").value,
      facebook: $("inputFb").value,
      instagram: $("inputIg").value
    };
    
    $("saveEditBtn").disabled = true;
    $("saveEditBtn").textContent = "Saving...";
    
    fetch(window.location.href, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify(payload)
    }).then(r => {
      if (!r.ok) throw new Error("Failed to update profile.");
      return r.json();
    }).then(data => {
      window.location.reload();
    }).catch(err => {
      $("editError").textContent = err.message;
      $("saveEditBtn").disabled = false;
      $("saveEditBtn").textContent = "Save Changes";
    });
  });
}

// Execute Rendering
renderProfile(profile);
renderRating(rating);