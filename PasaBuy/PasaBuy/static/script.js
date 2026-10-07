document.addEventListener('DOMContentLoaded', () => {
  const tabSignIn = document.getElementById('tab-signin');
  const tabLogIn = document.getElementById('tab-login');
  const viewSignIn = document.getElementById('view-signin');
  const viewLogIn = document.getElementById('view-login');
  const togglePasswordBtn = document.getElementById('toggle-password-btn');
  const passwordInput = document.getElementById('login-password');

  // Tab Switcher Handler
  function switchTab(activeTab) {
    if (activeTab === 'signin') {
      tabSignIn.classList.add('active');
      tabLogIn.classList.remove('active');
      
      viewSignIn.classList.add('active');
      viewLogIn.classList.remove('active');
    } else {
      tabLogIn.classList.add('active');
      tabSignIn.classList.remove('active');
      
      viewLogIn.classList.add('active');
      viewSignIn.classList.remove('active');
    }
  }

  // Event Listeners for Tab Buttons
  tabSignIn.addEventListener('click', () => switchTab('signin'));
  tabLogIn.addEventListener('click', () => switchTab('login'));

  // Toggle Password Visibility Handler
  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
    });
  }
});