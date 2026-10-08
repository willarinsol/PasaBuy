document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".page");
  const tabSignUp = document.getElementById("tab-signup");
  const tabLogIn = document.getElementById("tab-login");
  const viewSignUp = document.getElementById("view-signup");
  const viewLogIn = document.getElementById("view-login");
  const signupDetailsForm = document.getElementById("signup-details-form");
  const signupIdForm = document.getElementById("signup-id-form");
  const signupStepOne = document.getElementById("signup-step-1");
  const signupStepTwo = document.getElementById("signup-step-2");
  const backToDetails = document.getElementById("back-to-details");
  const togglePasswordBtn = document.getElementById("toggle-password-btn");
  const passwordInput = document.getElementById("login-password");
  const roleSelect = document.getElementById("role");
  const graduationGroup = document.querySelector(".graduation");
  const graduationInput = document.getElementById("graduation");

  function updateGraduationField() {
    const isStudent = roleSelect.value === "Student";
    graduationGroup.hidden = !isStudent;
    graduationInput.required = isStudent;

    if (!isStudent) {
      graduationInput.value = "";
    }
  }

  if (roleSelect) {
    roleSelect.addEventListener("change", updateGraduationField);
    updateGraduationField();
  }

  function switchTab(activeTab) {
    if (activeTab === "signup") {
      tabSignUp.classList.add("active");
      tabLogIn.classList.remove("active");

      viewSignUp.classList.add("active");
      viewLogIn.classList.remove("active");
    } else {
      tabLogIn.classList.add("active");
      tabSignUp.classList.remove("active");

      viewLogIn.classList.add("active");
      viewSignUp.classList.remove("active");
    }
  }

  function showSignupStep(step) {
    signupStepOne.hidden = step !== 1;
    signupStepTwo.hidden = step !== 2;
  }

  tabSignUp.addEventListener("click", () => switchTab("signup"));
  tabLogIn.addEventListener("click", () => switchTab("login"));

  signupDetailsForm.addEventListener("submit", (event) => {
    if (!signupDetailsForm.checkValidity()) {
      event.preventDefault();
    }
  });

  backToDetails.addEventListener("click", () => showSignupStep(1));

  signupIdForm.addEventListener("submit", (event) => {
    if (!signupIdForm.checkValidity()) {
      event.preventDefault();
    }
  });

  if (page.dataset.initialView === "signup") {
    switchTab("signup");
    showSignupStep(1);
  } else if (page.dataset.initialView === "upload") {
    switchTab("signup");
    showSignupStep(2);
  }

  // Toggle Password Visibility Handler
  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener("click", () => {
      const type =
        passwordInput.getAttribute("type") === "password" ? "text" : "password";
      passwordInput.setAttribute("type", type);
    });
  }
});
