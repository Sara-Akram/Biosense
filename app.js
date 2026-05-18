/* ============================================================
   ILM — App Controller
   Role-based login, splash transition, page routing
   ============================================================ */

const ILM = (() => {

  let currentRole = 'teacher';
  let currentPage = 'dashboard';

  const splash      = document.getElementById('splash');
  const app         = document.getElementById('app');
  const pageContent = document.getElementById('page-content');
  const splashLogin = document.getElementById('splash-login');

  /* ── Show login panel after video ends ── */
  function showLogin() {
    splashLogin.classList.add('visible');
  }

  /* ── Role selected → enter app ── */
  function selectRole(role) {
    currentRole = role;

    // Update nav role badge
    const badge = document.getElementById('nav-role-badge');
    const labels = { teacher: 'Teacher', student: 'Student', admin: 'Admin' };
    if (badge) badge.textContent = labels[role] || role;

    // Update nav tabs based on role
    const navTabs = document.querySelector('.nav-tabs');
    if (navTabs) {
      if (role === 'student') {
        navTabs.innerHTML = `
          <button class="nav-tab active" data-page="student">Dashboard</button>
          <button class="nav-tab" data-page="sessions">Sessions</button>
          <button class="nav-tab" data-page="messages">Messages</button>`;
      } else if (role === 'admin') {
        navTabs.innerHTML = `
          <button class="nav-tab active" data-page="admin">Dashboard</button>
          <button class="nav-tab" data-page="students">Users</button>
          <button class="nav-tab" data-page="settings">Settings</button>`;
      } else {
        navTabs.innerHTML = `
          <button class="nav-tab active" data-page="dashboard">Dashboard</button>
          <button class="nav-tab" data-page="sessions">Sessions</button>
          <button class="nav-tab" data-page="students">Students</button>
          <button class="nav-tab" data-page="earnings">Earnings</button>`;
      }
    }

    // Transition splash out
    splash.classList.add('fade-out');
    setTimeout(() => {
      splash.style.display = 'none';
      app.removeAttribute('aria-hidden');
      app.classList.add('visible');
      const homePage = role === 'student' ? 'student' : role === 'admin' ? 'admin' : 'dashboard';
      render(homePage);
      syncNav(homePage);
    }, 900);
  }

  /* ── Navigate ── */
  function navigate(page) {
    if (!ILM_PAGES[page]) return;
    currentPage = page;
    render(page);
    syncNav(page);
    // Scroll to top
    if (pageContent) pageContent.scrollTop = 0;
  }

  /* ── Render ── */
  function render(page) {
    const html = ILM_PAGES[page] ? ILM_PAGES[page]() : '<p style="padding:32px;color:var(--muted)">Page not found.</p>';
    pageContent.innerHTML = html;
    // Run inline scripts
    pageContent.querySelectorAll('script').forEach(old => {
      const s = document.createElement('script');
      s.textContent = old.textContent;
      old.parentNode.replaceChild(s, old);
    });
  }

  /* ── Sync nav ── */
  function syncNav(page) {
    document.querySelectorAll('.nav-tab, .sidebar-item').forEach(el => {
      el.classList.toggle('active', el.dataset.page === page);
    });
  }

  /* ── Bind nav clicks ── */
  function bindNav() {
    document.addEventListener('click', e => {
      const btn = e.target.closest('[data-page]');
      if (!btn || splash.contains(btn)) return;
      navigate(btn.dataset.page);
    });
  }

  /* ── Init ── */
  function init() {
    bindNav();
    // Video ends → show login
    const vid = document.getElementById('splash-video');
    if (vid) {
      vid.addEventListener('ended', showLogin);
      setTimeout(showLogin, 7000); // fallback
    }
  }

  init();

  return { showApp: () => showLogin(), navigate, selectRole };

})();
