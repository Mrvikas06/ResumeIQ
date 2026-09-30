document.addEventListener('DOMContentLoaded', () => {
  const style = document.createElement('style');
  style.innerHTML = `
    .modal-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); display: none; align-items: center; justify-content: center; z-index: 1000; opacity: 0; transition: opacity 0.2s; }
    .modal-overlay.visible { display: flex; opacity: 1; }
    .modal-content { background: #fff; width: 400px; border-radius: 12px; padding: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); transform: scale(0.95); transition: transform 0.2s; }
    .modal-overlay.visible .modal-content { transform: scale(1); }
    .modal-header { font-size: 18px; font-weight: 700; color: var(--ink); margin-bottom: 16px; display:flex; justify-content:space-between; align-items:center;}
    .modal-close { cursor: pointer; color: var(--mute); background:none; border:none; font-size: 24px; line-height: 1;}
    .modal-close:hover { color: var(--primary); }
    .modal-body .field-label { margin-bottom: 6px; font-weight: 600; font-size: 13px;}
    .modal-body input, .modal-body select { width: 100%; padding: 10px; border: 1px solid var(--hairline); border-radius: 8px; margin-bottom: 16px; font-family:inherit; background:#fff; outline:none;}
    .modal-body input:focus, .modal-body select:focus { border-color: var(--primary); }
    .toast-container { position: fixed; bottom: 96px; right: 24px; display: flex; flex-direction: column; gap: 8px; z-index: 9999; }
    .toast { background: var(--surface-card, #fff); color: var(--ink, #111827); padding: 16px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 4px solid var(--primary, #e11d48); transform: translateX(120%); opacity: 0; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 500; }
    .toast.show { transform: translateX(0); opacity: 1; }
    
    .contact-fab { position: fixed; bottom: 24px; right: 24px; width: 56px; height: 56px; background: var(--ink, #111827); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(0,0,0,0.25); cursor: pointer; transition: transform 0.2s, background 0.2s; z-index: 9998; }
    .contact-fab:hover { transform: scale(1.05); background: var(--primary, #e11d48); color: #fff; }
    @media print { .contact-fab { display: none !important; } }
  `;
  document.head.appendChild(style);

  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.id = 'profileModal';
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <span>Edit Profile</span>
        <button class="modal-close" onclick="closeProfileModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div class="field-label">Display Name</div>
        <input type="text" id="profName">
        <div class="field-label">Target Role</div>
        <input type="text" id="profRole" placeholder="e.g. AI/ML Engineer">
        <div class="field-label">Experience Level</div>
        <select id="profExp">
          <option>Entry Level</option>
          <option>Mid Level</option>
          <option>Senior Level</option>
        </select>
        <button class="btn-primary" style="width:100%; justify-content:center; padding:12px; margin-top:8px;" onclick="saveProfile()">Save Changes</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  const saved = JSON.parse(localStorage.getItem('userProfile') || '{"name":"Vikas", "role":"AI/ML Engineer", "exp":"Mid Level"}');
  document.getElementById('profName').value = saved.name;
  document.getElementById('profRole').value = saved.role;
  document.getElementById('profExp').value = saved.exp || 'Mid Level';
  updateProfileNames(saved.name);

  // Bind the profile button correctly
  document.querySelectorAll('#profileBtn').forEach(btn => {
    btn.removeAttribute('onclick');
    btn.onclick = (e) => { e.preventDefault(); window.openProfileModal(); };
  });

  // Clock logic
  const clockEl = document.getElementById('topbarClock');
  if (clockEl) {
    setInterval(() => {
      clockEl.textContent = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }, 1000);
    clockEl.textContent = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  }

  // Search Logic
  const searchInput = document.querySelector('.topbar-search input');
  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.target.value.trim() !== '') {
        e.preventDefault();
        window.location.href = 'history.html?q=' + encodeURIComponent(e.target.value.trim());
      }
    });
  }

  // Initialize Usage Meter
  if (window.updateUsageMeter) window.updateUsageMeter();

  // Attach usage increment to main action buttons
  document.querySelectorAll('.btn-primary').forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.textContent.toLowerCase().includes('analyze') || btn.textContent.toLowerCase().includes('upload') || btn.textContent.toLowerCase().includes('match')) {
        window.incrementUsage();
        window.showToast('Analysis complete! 1 Scan used.');
      }
    });
  });

  // Inject Floating Contact Icon
  const contactFab = document.createElement('a');
  contactFab.href = "https://www.linkedin.com/in/vikas2106/"; 
  contactFab.target = "_blank";
  contactFab.title = "Connect on LinkedIn";
  contactFab.className = "contact-fab";
  contactFab.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>`;
  document.body.appendChild(contactFab);
});

// --- Toast Notifications ---
window.showToast = (msg) => {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary, #e11d48)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> ${msg}`;
  container.appendChild(toast);
  
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};

// --- Dynamic Usage Meter ---
window.updateUsageMeter = () => {
  const scansUsed = parseInt(sessionStorage.getItem('scansUsed') || '0');
  const maxScans = 10;
  document.querySelectorAll('.usage-meter').forEach(meter => {
    const textEl = meter.querySelector('.usage-text');
    const fillEl = meter.querySelector('.usage-bar-fill');
    if (textEl && fillEl) {
      textEl.textContent = `${scansUsed}/${maxScans} Scans`;
      fillEl.style.width = `${Math.min((scansUsed / maxScans) * 100, 100)}%`;
      meter.title = `${scansUsed}/${maxScans} Free Scans Used`;
    }
  });
};

window.incrementUsage = () => {
  let scans = parseInt(sessionStorage.getItem('scansUsed') || '0');
  if (scans < 10) {
    scans++;
    sessionStorage.setItem('scansUsed', scans.toString());
    updateUsageMeter();
  } else {
    window.showToast('You have reached your 10 scan limit!');
  }
};

window.openProfileModal = () => document.getElementById('profileModal').classList.add('visible');
window.closeProfileModal = () => document.getElementById('profileModal').classList.remove('visible');
window.saveProfile = () => {
  const name = document.getElementById('profName').value;
  const role = document.getElementById('profRole').value;
  const exp = document.getElementById('profExp').value;
  localStorage.setItem('userProfile', JSON.stringify({name, role, exp}));
  updateProfileNames(name);
  window.closeProfileModal();
};

window.updateProfileNames = (name) => {
  document.querySelectorAll('#profileBtn').forEach(btn => {
    if(btn.innerHTML.includes('<svg')) {
      btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg> ${name}`;
    }
  });
};
