/* ============================================================
   ILM — Page Templates (Teacher / Student / Admin + Classroom)
   ============================================================ */

window.ILM_PAGES = {

  /* ── TEACHER DASHBOARD ── */
  dashboard() {
    return `
      <div class="page-header">
        <div><h1>Good morning, <span style="color:var(--accent)">Sara</span></h1><p>Monday, May 18 · 3 sessions today</p></div>
        <button class="btn btn-primary" onclick="ILM.navigate('classroom')">+ Start Session</button>
      </div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-card-label">Sessions this week</div><div class="stat-card-value">12</div><div class="stat-card-sub">↑ 3 from last week</div></div>
        <div class="stat-card"><div class="stat-card-label">Active students</div><div class="stat-card-value">8</div><div class="stat-card-sub">↑ 1 new this month</div></div>
        <div class="stat-card"><div class="stat-card-label">Avg. session</div><div class="stat-card-value">54<span>m</span></div><div class="stat-card-sub neutral">Steady</div></div>
        <div class="stat-card"><div class="stat-card-label">Rating</div><div class="stat-card-value">4.9★</div><div class="stat-card-sub">41 reviews</div></div>
      </div>
      <div class="two-col">
        <div class="card">
          <div class="card-header"><span class="card-title">Today's sessions</span><span class="card-action" onclick="ILM.navigate('sessions')">View all →</span></div>
          ${[
            {av:'av-amber', i:'E', name:'Emma Thompson',  sub:'Biology · Grade 10',  badge:'badge-live',     bt:'● Live',    t:'2:00 – 3:00 PM'},
            {av:'av-warm',  i:'L', name:'Lucas Bennett',  sub:'Chemistry · Grade 11', badge:'badge-upcoming', bt:'Upcoming',  t:'4:00 – 5:00 PM'},
            {av:'av-rose',  i:'S', name:'Sophie Miller',  sub:'Math · Grade 8',       badge:'badge-done',     bt:'Done',      t:'10:00 – 11:00 AM'},
            {av:'av-blue',  i:'J', name:'Jake Harrison',  sub:'English · Grade 6',    badge:'badge-upcoming', bt:'Upcoming',  t:'6:00 – 7:00 PM'},
          ].map(s=>`
            <div class="session-row">
              <div class="s-avatar ${s.av}">${s.i}</div>
              <div class="s-info"><div class="s-name">${s.name}</div><div class="s-sub">${s.sub}</div></div>
              <div class="s-time"><span class="badge ${s.badge}">${s.bt}</span><br>${s.t}</div>
            </div>`).join('')}
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">Earnings</span><span style="font-size:11px;color:var(--muted)">May 2026</span></div>
          <div class="earn-body">
            <div class="earn-total">$1,240</div>
            <div class="earn-sub">31 sessions completed</div>
            <div class="earn-row"><span class="earn-row-label">This week</span><span class="earn-row-val">$380</span></div>
            <div class="earn-row"><span class="earn-row-label">Pending</span><span class="earn-row-val">$220</span></div>
            <div class="earn-row"><span class="earn-row-label">Platform fee (15%)</span><span class="earn-row-val negative">−$57</span></div>
            <div class="earn-row"><span class="earn-row-label">Next payout</span><span class="earn-row-val positive">May 23</span></div>
            <button class="btn btn-primary" style="width:100%;margin-top:16px;border-radius:10px;justify-content:center;">Request early payout</button>
          </div>
        </div>
      </div>`;
  },

  /* ── STUDENT DASHBOARD ── */
  student() {
    return `
      <div class="page-header">
        <div><h1>Hello, <span style="color:var(--accent)">Emma</span></h1><p>Monday, May 18 · 1 session today</p></div>
        <button class="btn btn-primary" onclick="ILM.navigate('classroom')">Join Session</button>
      </div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-card-label">Sessions completed</div><div class="stat-card-value">24</div><div class="stat-card-sub">This month</div></div>
        <div class="stat-card"><div class="stat-card-label">Subjects</div><div class="stat-card-value">3</div><div class="stat-card-sub neutral">Biology, Math, English</div></div>
        <div class="stat-card"><div class="stat-card-label">Progress</div><div class="stat-card-value">82<span>%</span></div><div class="stat-card-sub">↑ 6% this week</div></div>
        <div class="stat-card"><div class="stat-card-label">Streak</div><div class="stat-card-value">7<span>d</span></div><div class="stat-card-sub">Keep it up!</div></div>
      </div>
      <div class="two-col">
        <div class="card">
          <div class="card-header"><span class="card-title">Upcoming sessions</span></div>
          ${[
            {av:'av-warm', i:'S', name:'Sara A.',       sub:'Biology · Today 2:00 PM',    badge:'badge-live',     bt:'● Live now'},
            {av:'av-warm', i:'S', name:'Sara A.',       sub:'Math · Tomorrow 3:00 PM',    badge:'badge-upcoming', bt:'Tomorrow'},
            {av:'av-blue', i:'M', name:'Mr. Collins',   sub:'English · Thu 4:00 PM',      badge:'badge-upcoming', bt:'Thursday'},
          ].map(s=>`
            <div class="session-row">
              <div class="s-avatar ${s.av}">${s.i}</div>
              <div class="s-info"><div class="s-name">${s.name}</div><div class="s-sub">${s.sub}</div></div>
              <div class="s-time"><span class="badge ${s.badge}">${s.bt}</span></div>
            </div>`).join('')}
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">My progress</span></div>
          <div style="padding:18px 20px;display:flex;flex-direction:column;gap:14px;">
            ${[
              {sub:'Biology', pct:82},
              {sub:'Mathematics', pct:67},
              {sub:'English', pct:91},
            ].map(p=>`
              <div>
                <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:6px;">
                  <span style="font-weight:500">${p.sub}</span>
                  <span style="color:var(--muted)">${p.pct}%</span>
                </div>
                <div style="height:6px;background:var(--border-mid);border-radius:99px;overflow:hidden;">
                  <div style="height:100%;width:${p.pct}%;background:var(--ink);border-radius:99px;"></div>
                </div>
              </div>`).join('')}
          </div>
        </div>
      </div>`;
  },

  /* ── ADMIN DASHBOARD ── */
  admin() {
    return `
      <div class="page-header">
        <div><h1>Admin Overview</h1><p>Monday, May 18 · Platform summary</p></div>
        <button class="btn btn-primary">+ Add User</button>
      </div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-card-label">Total teachers</div><div class="stat-card-value">48</div><div class="stat-card-sub">↑ 4 this month</div></div>
        <div class="stat-card"><div class="stat-card-label">Total students</div><div class="stat-card-value">312</div><div class="stat-card-sub">↑ 28 this month</div></div>
        <div class="stat-card"><div class="stat-card-label">Sessions today</div><div class="stat-card-value">87</div><div class="stat-card-sub neutral">Live right now: 23</div></div>
        <div class="stat-card"><div class="stat-card-label">Revenue (May)</div><div class="stat-card-value">$18k</div><div class="stat-card-sub">↑ 12% from Apr</div></div>
      </div>
      <div class="card" style="margin-bottom:18px;">
        <div class="card-header"><span class="card-title">Recent signups</span><span class="card-action">View all →</span></div>
        <table class="data-table">
          <thead><tr><th>Name</th><th>Role</th><th>Joined</th><th>Status</th></tr></thead>
          <tbody>
            ${[
              {n:'Emma Thompson',  r:'Student', d:'May 17', s:'Active'},
              {n:'Mr. James Cole', r:'Teacher', d:'May 16', s:'Pending'},
              {n:'Sophie Miller',  r:'Student', d:'May 15', s:'Active'},
              {n:'Lucas Bennett',  r:'Student', d:'May 14', s:'Active'},
              {n:'Dr. Anne Walsh', r:'Teacher', d:'May 13', s:'Active'},
            ].map(u=>`
              <tr>
                <td class="td-name">${u.n}</td>
                <td class="td-muted">${u.r}</td>
                <td class="td-muted">${u.d}</td>
                <td><span class="badge ${u.s==='Active'?'badge-live':'badge-upcoming'}">${u.s}</span></td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="two-col">
        <div class="card">
          <div class="card-header"><span class="card-title">Live sessions now</span></div>
          ${[
            {t:'Biology · Grade 10', teacher:'Sara A.', students:4},
            {t:'Math · Grade 8',     teacher:'Mr. Cole', students:2},
            {t:'English · Grade 6',  teacher:'Ms. Park', students:3},
          ].map(s=>`
            <div class="session-row">
              <div style="flex:1;"><div class="s-name">${s.t}</div><div class="s-sub">Teacher: ${s.teacher}</div></div>
              <div class="s-time"><span class="badge badge-live">● Live</span><br>${s.students} students</div>
            </div>`).join('')}
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">Platform health</span></div>
          <div class="earn-body">
            <div class="earn-row"><span class="earn-row-label">Uptime</span><span class="earn-row-val positive">99.9%</span></div>
            <div class="earn-row"><span class="earn-row-label">Avg. session quality</span><span class="earn-row-val">4.8★</span></div>
            <div class="earn-row"><span class="earn-row-label">Support tickets open</span><span class="earn-row-val">3</span></div>
            <div class="earn-row"><span class="earn-row-label">Failed payments</span><span class="earn-row-val">1</span></div>
          </div>
        </div>
      </div>`;
  },

  /* ── SESSIONS ── */
  sessions() {
    return `
      <div class="page-header">
        <div><h1>Sessions</h1><p>Manage your schedule</p></div>
        <button class="btn btn-primary">+ Book Session</button>
      </div>
      <div class="card">
        <div class="card-header"><span class="card-title">All sessions</span>
          <div style="display:flex;gap:8px;">
            <button class="btn btn-outline btn-sm">Today</button>
            <button class="btn btn-outline btn-sm">This week</button>
          </div>
        </div>
        ${[
          {av:'av-amber', i:'E', name:'Emma Thompson',  sub:'Biology · Grade 10',   badge:'badge-live',     bt:'● Live',   t:'Today · 2:00 – 3:00 PM'},
          {av:'av-warm',  i:'L', name:'Lucas Bennett',  sub:'Chemistry · Grade 11', badge:'badge-upcoming', bt:'Upcoming', t:'Today · 4:00 – 5:00 PM'},
          {av:'av-blue',  i:'J', name:'Jake Harrison',  sub:'English · Grade 6',    badge:'badge-upcoming', bt:'Upcoming', t:'Today · 6:00 – 7:00 PM'},
          {av:'av-rose',  i:'S', name:'Sophie Miller',  sub:'Math · Grade 8',       badge:'badge-done',     bt:'Done',     t:'Today · 10:00 – 11:00 AM'},
          {av:'av-purple',i:'O', name:'Olivia Carter',  sub:'Physics · Grade 12',   badge:'badge-done',     bt:'Done',     t:'Yesterday · 3:00 PM'},
        ].map(s=>`
          <div class="session-row">
            <div class="s-avatar ${s.av}">${s.i}</div>
            <div class="s-info"><div class="s-name">${s.name}</div><div class="s-sub">${s.sub}</div></div>
            <div class="s-time"><span class="badge ${s.badge}">${s.bt}</span><br>${s.t}</div>
            <button class="btn btn-outline btn-sm" style="margin-left:12px;" onclick="ILM.navigate('classroom')">Join</button>
          </div>`).join('')}
      </div>`;
  },

  /* ── STUDENTS ── */
  students() {
    const list = [
      {av:'av-amber', i:'E', name:'Emma Thompson',  grade:'Grade 10', sub:'Biology',   n:12, p:82, s:'Active'},
      {av:'av-warm',  i:'L', name:'Lucas Bennett',  grade:'Grade 11', sub:'Chemistry', n:8,  p:67, s:'Active'},
      {av:'av-rose',  i:'S', name:'Sophie Miller',  grade:'Grade 8',  sub:'Math',      n:15, p:91, s:'Active'},
      {av:'av-blue',  i:'J', name:'Jake Harrison',  grade:'Grade 6',  sub:'English',   n:6,  p:55, s:'Active'},
      {av:'av-purple',i:'O', name:'Olivia Carter',  grade:'Grade 12', sub:'Physics',   n:20, p:95, s:'Active'},
      {av:'av-warm',  i:'N', name:'Noah Williams',  grade:'Grade 9',  sub:'Math',      n:3,  p:40, s:'New'},
      {av:'av-rose',  i:'C', name:'Chloe Davis',    grade:'Grade 7',  sub:'English',   n:9,  p:73, s:'Active'},
    ];
    return `
      <div class="page-header">
        <div><h1>Students</h1><p>${list.length} students in your roster</p></div>
        <button class="btn btn-primary">+ Add Student</button>
      </div>
      <div class="card">
        <table class="data-table">
          <thead><tr><th>Student</th><th>Subject</th><th>Sessions</th><th>Progress</th><th>Status</th></tr></thead>
          <tbody>
            ${list.map(s=>`
              <tr>
                <td><div style="display:flex;align-items:center;gap:10px;">
                  <div class="s-avatar ${s.av}" style="width:30px;height:30px;font-size:11px;">${s.i}</div>
                  <div><div class="td-name">${s.name}</div><div class="td-muted" style="font-size:11px;">${s.grade}</div></div>
                </div></td>
                <td class="td-muted">${s.sub}</td>
                <td>${s.n}</td>
                <td><div style="display:flex;align-items:center;gap:8px;">
                  <div class="progress-bar"><div class="progress-fill" style="width:${s.p}%"></div></div>
                  <span style="font-size:11px;color:var(--muted)">${s.p}%</span>
                </div></td>
                <td><span class="badge ${s.s==='Active'?'badge-live':'badge-new'}">${s.s}</span></td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  },

  /* ── EARNINGS ── */
  earnings() {
    return `
      <div class="page-header">
        <div><h1>Earnings</h1><p>Track income and payouts</p></div>
        <button class="btn btn-outline">Download report</button>
      </div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-card-label">This month</div><div class="stat-card-value">$1,240</div><div class="stat-card-sub">↑ $180 from April</div></div>
        <div class="stat-card"><div class="stat-card-label">This week</div><div class="stat-card-value">$380</div><div class="stat-card-sub neutral">12 sessions</div></div>
        <div class="stat-card"><div class="stat-card-label">Pending</div><div class="stat-card-value">$220</div><div class="stat-card-sub neutral">Pays May 23</div></div>
        <div class="stat-card"><div class="stat-card-label">All time</div><div class="stat-card-value">$8.4k</div><div class="stat-card-sub">Since Jan 2026</div></div>
      </div>
      <div class="two-col">
        <div class="card">
          <div class="card-header"><span class="card-title">Recent payouts</span></div>
          ${[
            {d:'May 16',amt:'$320',n:10},{d:'May 9',amt:'$290',n:9},{d:'May 2',amt:'$350',n:11},{d:'Apr 25',amt:'$280',n:9}
          ].map(p=>`
            <div class="session-row">
              <div style="flex:1"><div class="s-name">${p.d}, 2026</div><div class="s-sub">${p.n} sessions</div></div>
              <div style="text-align:right"><div style="font-weight:500;font-size:15px">${p.amt}</div><span class="badge badge-live">Paid</span></div>
            </div>`).join('')}
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">Payout settings</span></div>
          <div class="earn-body">
            <div class="earn-row"><span class="earn-row-label">Rate per hour</span><span class="earn-row-val">$40</span></div>
            <div class="earn-row"><span class="earn-row-label">Platform fee</span><span class="earn-row-val negative">15%</span></div>
            <div class="earn-row"><span class="earn-row-label">Schedule</span><span class="earn-row-val">Weekly (Fri)</span></div>
            <div class="earn-row"><span class="earn-row-label">Method</span><span class="earn-row-val">Direct deposit</span></div>
            <button class="btn btn-outline" style="width:100%;margin-top:16px;border-radius:10px;justify-content:center;">Edit payout method</button>
          </div>
        </div>
      </div>`;
  },

  /* ── CLASSROOM ── */
  classroom() {
    return `
      <div class="classroom-wrap">

        <!-- Header -->
        <div class="classroom-header">
          <div>
            <div class="classroom-title">Biology · Grade 10 — Emma Thompson</div>
            <div class="classroom-time" id="session-timer">Session time: 00:00</div>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn btn-outline btn-sm" style="color:#e8e0d0;border-color:rgba(255,255,255,0.15);" onclick="togglePdfOverlay()">
              <svg viewBox="0 0 24 24" style="width:13px;height:13px;stroke:#e8e0d0"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Upload PDF
            </button>
            <button class="btn btn-danger btn-sm" onclick="ILM.navigate('sessions')">End Session</button>
          </div>
        </div>

        <!-- Whiteboard area -->
        <div class="classroom-main">
          <!-- PDF overlay -->
          <div id="pdf-overlay">
            <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:20px;">
              <img id="pdf-img" src="" alt="PDF page" style="max-height:100%;max-width:100%;object-fit:contain;opacity:0.4;border-radius:4px;">
            </div>
          </div>

          <!-- Toolbar -->
          <div class="wb-toolbar">
            <button class="wb-btn active" id="tool-pen" onclick="setTool('pen')" title="Pen">
              <svg viewBox="0 0 24 24"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </button>
            <button class="wb-btn" id="tool-highlight" onclick="setTool('highlight')" title="Highlighter">
              <svg viewBox="0 0 24 24"><path d="M9 11l3 3 8-8"/><path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9"/></svg>
            </button>
            <button class="wb-btn" id="tool-arrow" onclick="setTool('arrow')" title="Arrow">
              <svg viewBox="0 0 24 24"><line x1="5" y1="19" x2="19" y2="5"/><polyline points="12 5 19 5 19 12"/></svg>
            </button>
            <button class="wb-btn" id="tool-text" onclick="setTool('text')" title="Text">
              <svg viewBox="0 0 24 24"><polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/></svg>
            </button>
            <button class="wb-btn" id="tool-shape" onclick="setTool('rect')" title="Rectangle">
              <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            </button>
            <div class="wb-sep"></div>
            <button class="wb-btn" id="tool-eraser" onclick="setTool('eraser')" title="Eraser">
              <svg viewBox="0 0 24 24"><path d="M20 20H7L3 16l13-13 6 6-2 2"/></svg>
            </button>
            <button class="wb-btn" onclick="clearCanvas()" title="Clear all">
              <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/></svg>
            </button>
            <button class="wb-btn" onclick="undoCanvas()" title="Undo">
              <svg viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.64"/></svg>
            </button>
            <div class="wb-sep"></div>
            <span class="wb-label">Color</span>
            ${['#1a1410','#8b2a2a','#2a4a8b','#2a6b3a','#8b6f2a'].map((c,i)=>`
              <div class="color-dot ${i===0?'selected':''}" style="background:${c}" data-color="${c}" onclick="setColor('${c}',this)" title="${c}"></div>`).join('')}
            <div class="wb-sep"></div>
            <span class="wb-label">Size</span>
            <input type="range" min="1" max="24" value="3" style="width:70px;accent-color:#e8e0d0;" oninput="setBrushSize(this.value)">
          </div>

          <!-- Canvas -->
          <canvas id="wb-canvas"></canvas>
        </div>

        <!-- Sidebar: participants + chat -->
        <div class="classroom-sidebar">
          <div class="cs-tabs">
            <div class="cs-tab active" onclick="switchCsTab('participants',this)">Participants</div>
            <div class="cs-tab" onclick="switchCsTab('chat',this)">Chat</div>
          </div>

          <div class="cs-panel active" id="panel-participants">
            ${[
              {i:'SA', name:'Sara A. (You)', role:'Teacher', mic:true,  cam:true},
              {i:'ET', name:'Emma Thompson', role:'Student', mic:true,  cam:false},
              {i:'LB', name:'Lucas Bennett', role:'Student', mic:false, cam:false},
              {i:'SM', name:'Sophie Miller', role:'Student', mic:true,  cam:true},
            ].map(p=>`
              <div class="participant-row">
                <div class="p-avatar">${p.i}</div>
                <div style="flex:1"><div class="p-name">${p.name}</div><div class="p-role">${p.role}</div></div>
                <div class="p-icons">
                  <div class="p-icon ${p.mic?'on':''}">
                    <svg viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                  </div>
                  <div class="p-icon ${p.cam?'on':''}">
                    <svg viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
                  </div>
                </div>
              </div>`).join('')}
          </div>

          <div class="cs-panel" id="panel-chat" style="flex-direction:column;gap:0;">
            <div class="chat-messages" id="chat-messages">
              <div class="chat-msg"><div class="chat-sender">Emma Thompson</div><div class="chat-text">Can we review the diagram on slide 3?</div></div>
              <div class="chat-msg"><div class="chat-sender">Sara A.</div><div class="chat-text">Sure, let me pull it up on the board now.</div></div>
              <div class="chat-msg"><div class="chat-sender">Sophie Miller</div><div class="chat-text">I have a question about DNA replication</div></div>
            </div>
            <div class="chat-input-row">
              <input class="chat-input" id="chat-input" type="text" placeholder="Type a message…">
              <button class="chat-send" onclick="sendChat()">Send</button>
            </div>
          </div>
        </div>

        <!-- Video strip -->
        <div class="classroom-footer">
          ${[
            {i:'SA', name:'You',    self:true},
            {i:'ET', name:'Emma',   self:false},
            {i:'LB', name:'Lucas',  self:false},
            {i:'SM', name:'Sophie', self:false},
          ].map(v=>`
            <div class="video-tile ${v.self?'self':''}">
              <div class="vt-avatar">${v.i}</div>
              <div class="vt-name">${v.name}</div>
            </div>`).join('')}
          <div style="flex:1"></div>
        </div>

        <!-- Controls -->
        <div class="classroom-controls">
          <div class="ctrl-btn active" onclick="this.classList.toggle('active')" title="Mute">
            <svg viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
            <span class="ctrl-label">Mic</span>
          </div>
          <div class="ctrl-btn active" onclick="this.classList.toggle('active')" title="Camera">
            <svg viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
            <span class="ctrl-label">Camera</span>
          </div>
          <div class="ctrl-btn" onclick="this.classList.toggle('active')" title="Screen share">
            <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <span class="ctrl-label">Share</span>
          </div>
          <div class="ctrl-btn" onclick="this.classList.toggle('active')" title="Raise hand">
            <svg viewBox="0 0 24 24"><path d="M18 11V6a2 2 0 0 0-4 0v5M14 10V4a2 2 0 0 0-4 0v6M10 10.5V6a2 2 0 0 0-4 0v8l-1-1a2 2 0 0 0-3 3l4 4a6 6 0 0 0 6 0 6 6 0 0 0 6-6v-2a2 2 0 0 0-4 0"/></svg>
            <span class="ctrl-label">Hand</span>
          </div>
          <div class="ctrl-btn danger" onclick="ILM.navigate('sessions')" title="Leave">
            <svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            <span class="ctrl-label">Leave</span>
          </div>
        </div>

      </div>

      <script>
      (function() {
        // ── Canvas setup ──
        const canvas = document.getElementById('wb-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let tool = 'pen', color = '#1a1410', size = 3;
        let drawing = false, history = [], startX, startY;

        function resize() {
          const data = ctx.getImageData(0,0,canvas.width,canvas.height);
          canvas.width  = canvas.parentElement.clientWidth;
          canvas.height = canvas.parentElement.clientHeight - canvas.previousElementSibling.offsetHeight - (document.getElementById('pdf-overlay') ? 0 : 0);
          ctx.putImageData(data,0,0);
        }
        resize();
        window.addEventListener('resize', resize);

        function getPos(e) {
          const r = canvas.getBoundingClientRect();
          const src = e.touches ? e.touches[0] : e;
          return { x: src.clientX - r.left, y: src.clientY - r.top };
        }

        function save() { history.push(ctx.getImageData(0,0,canvas.width,canvas.height)); if(history.length>40) history.shift(); }

        canvas.addEventListener('mousedown', e => {
          drawing = true; save();
          const p = getPos(e); startX = p.x; startY = p.y;
          if (tool === 'pen' || tool === 'eraser' || tool === 'highlight') {
            ctx.beginPath(); ctx.moveTo(p.x, p.y);
          }
        });

        canvas.addEventListener('mousemove', e => {
          if (!drawing) return;
          const p = getPos(e);
          if (tool === 'pen') {
            ctx.globalCompositeOperation = 'source-over';
            ctx.globalAlpha = 1;
            ctx.strokeStyle = color; ctx.lineWidth = size;
            ctx.lineCap = 'round'; ctx.lineJoin = 'round';
            ctx.lineTo(p.x, p.y); ctx.stroke();
          } else if (tool === 'eraser') {
            ctx.globalCompositeOperation = 'destination-out';
            ctx.lineWidth = size * 4; ctx.lineCap = 'round';
            ctx.lineTo(p.x, p.y); ctx.stroke();
            ctx.globalCompositeOperation = 'source-over';
          } else if (tool === 'highlight') {
            ctx.globalCompositeOperation = 'source-over';
            ctx.globalAlpha = 0.3;
            ctx.strokeStyle = '#f5c842'; ctx.lineWidth = size * 5;
            ctx.lineCap = 'square';
            ctx.lineTo(p.x, p.y); ctx.stroke();
            ctx.globalAlpha = 1;
          }
        });

        canvas.addEventListener('mouseup', e => {
          if (!drawing) return;
          drawing = false;
          const p = getPos(e);
          if (tool === 'rect') {
            ctx.globalCompositeOperation = 'source-over';
            ctx.globalAlpha = 1;
            ctx.strokeStyle = color; ctx.lineWidth = size;
            ctx.strokeRect(startX, startY, p.x - startX, p.y - startY);
          } else if (tool === 'arrow') {
            ctx.globalCompositeOperation = 'source-over';
            ctx.globalAlpha = 1;
            ctx.strokeStyle = color; ctx.lineWidth = size;
            ctx.beginPath(); ctx.moveTo(startX, startY); ctx.lineTo(p.x, p.y); ctx.stroke();
            // arrowhead
            const angle = Math.atan2(p.y - startY, p.x - startX);
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.x - 12 * Math.cos(angle - 0.4), p.y - 12 * Math.sin(angle - 0.4));
            ctx.lineTo(p.x - 12 * Math.cos(angle + 0.4), p.y - 12 * Math.sin(angle + 0.4));
            ctx.closePath(); ctx.fillStyle = color; ctx.fill();
          }
        });

        canvas.addEventListener('mouseleave', () => { drawing = false; });

        // Touch support
        canvas.addEventListener('touchstart', e => { e.preventDefault(); canvas.dispatchEvent(new MouseEvent('mousedown', {clientX: e.touches[0].clientX, clientY: e.touches[0].clientY})); });
        canvas.addEventListener('touchmove',  e => { e.preventDefault(); canvas.dispatchEvent(new MouseEvent('mousemove', {clientX: e.touches[0].clientX, clientY: e.touches[0].clientY})); });
        canvas.addEventListener('touchend',   e => { e.preventDefault(); canvas.dispatchEvent(new MouseEvent('mouseup',   {clientX: e.changedTouches[0].clientX, clientY: e.changedTouches[0].clientY})); });

        // Global tool functions
        window.setTool = t => {
          tool = t;
          document.querySelectorAll('.wb-btn[id^=tool]').forEach(b => b.classList.remove('active'));
          const btn = document.getElementById('tool-' + t);
          if (btn) btn.classList.add('active');
        };
        window.setColor = (c, el) => {
          color = c;
          document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('selected'));
          el.classList.add('selected');
        };
        window.setBrushSize = v => { size = +v; };
        window.clearCanvas  = () => { save(); ctx.clearRect(0,0,canvas.width,canvas.height); };
        window.undoCanvas   = () => { if (history.length) ctx.putImageData(history.pop(),0,0); };

        // PDF overlay toggle (simulated)
        window.togglePdfOverlay = () => {
          const overlay = document.getElementById('pdf-overlay');
          if (!overlay) return;
          if (overlay.classList.contains('visible')) {
            overlay.classList.remove('visible');
          } else {
            overlay.classList.add('visible');
            // draw a sample grid to simulate PDF
            const img = document.getElementById('pdf-img');
            const tmpCanvas = document.createElement('canvas');
            tmpCanvas.width = 600; tmpCanvas.height = 800;
            const tc = tmpCanvas.getContext('2d');
            tc.fillStyle = '#fff'; tc.fillRect(0,0,600,800);
            tc.strokeStyle = '#ccc'; tc.lineWidth = 1;
            for(let y=60;y<800;y+=40){tc.beginPath();tc.moveTo(40,y);tc.lineTo(560,y);tc.stroke();}
            tc.fillStyle = '#333'; tc.font = 'bold 22px serif';
            tc.fillText('Biology — Chapter 4: DNA Replication', 40, 40);
            tc.font = '16px sans-serif'; tc.fillStyle = '#555';
            tc.fillText('1. The double helix unwinds at the origin of replication.', 40, 100);
            tc.fillText('2. Helicase breaks the hydrogen bonds between base pairs.', 40, 140);
            tc.fillText('3. Primase adds RNA primers to initiate synthesis.', 40, 180);
            tc.fillText('4. DNA polymerase III extends the new strand 5\'→3\'.', 40, 220);
            img.src = tmpCanvas.toDataURL();
          }
        };

        // Sidebar tab switch
        window.switchCsTab = (tab, el) => {
          document.querySelectorAll('.cs-tab').forEach(t => t.classList.remove('active'));
          document.querySelectorAll('.cs-panel').forEach(p => p.classList.remove('active'));
          el.classList.add('active');
          const panel = document.getElementById('panel-' + tab);
          if (panel) panel.classList.add('active');
        };

        // Chat send
        window.sendChat = () => {
          const input = document.getElementById('chat-input');
          if (!input || !input.value.trim()) return;
          const msgs = document.getElementById('chat-messages');
          const div = document.createElement('div');
          div.className = 'chat-msg';
          div.innerHTML = '<div class="chat-sender">Sara A.</div><div class="chat-text">' + input.value + '</div>';
          msgs.appendChild(div);
          msgs.scrollTop = msgs.scrollHeight;
          input.value = '';
        };
        document.getElementById('chat-input')?.addEventListener('keydown', e => { if(e.key==='Enter') sendChat(); });

        // Session timer
        let sec = 0;
        const timerEl = document.getElementById('session-timer');
        const interval = setInterval(() => {
          if (!document.getElementById('session-timer')) { clearInterval(interval); return; }
          sec++;
          const m = String(Math.floor(sec/60)).padStart(2,'0');
          const s2 = String(sec%60).padStart(2,'0');
          timerEl.textContent = 'Session time: ' + m + ':' + s2;
        }, 1000);

      })();
      <\/script>`;
  },

  /* ── MESSAGES ── */
  messages() {
    return `
      <div class="page-header"><div><h1>Messages</h1><p>Chat with students and parents</p></div></div>
      <div class="two-col" style="align-items:start;">
        <div class="card">
          ${[
            {av:'av-amber', i:'E', name:'Emma Thompson',  preview:'Can we review chapter 4 today?', time:'2:14 PM', unread:true},
            {av:'av-warm',  i:'L', name:'Lucas Bennett',  preview:'Thanks for the notes!',          time:'1:05 PM', unread:false},
            {av:'av-blue',  i:'J', name:'Jake Harrison',  preview:"I'll be 5 minutes late",         time:'12:50 PM',unread:false},
            {av:'av-rose',  i:'S', name:'Sophie Miller',  preview:'Great session today',            time:'Yesterday',unread:false},
          ].map(m=>`
            <div class="session-row" style="cursor:pointer">
              <div class="s-avatar ${m.av}">${m.i}</div>
              <div class="s-info"><div class="s-name" style="${m.unread?'font-weight:600':''}">${m.name}</div><div class="s-sub">${m.preview}</div></div>
              <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                <span style="font-size:11px;color:var(--muted)">${m.time}</span>
                ${m.unread?'<span style="width:7px;height:7px;border-radius:50%;background:var(--ink);display:block;"></span>':''}
              </div>
            </div>`).join('')}
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">Emma Thompson</span><span class="badge badge-live">● Live session</span></div>
          <div style="padding:16px;min-height:280px;display:flex;flex-direction:column;gap:10px;">
            <div style="background:var(--paper-dark);border-radius:10px 10px 10px 3px;padding:9px 13px;font-size:13px;max-width:80%;border:1px solid var(--border)">Can we review chapter 4 today?</div>
            <div style="background:var(--ink);color:var(--paper);border-radius:10px 10px 3px 10px;padding:9px 13px;font-size:13px;max-width:80%;align-self:flex-end">Of course! Let's start with DNA replication.</div>
          </div>
          <div style="padding:10px 14px;border-top:1px solid var(--border);display:flex;gap:8px;">
            <input type="text" placeholder="Type a message…" style="flex:1;font-family:'DM Sans',sans-serif;font-size:13px;border:1px solid var(--border-mid);border-radius:6px;padding:9px 13px;outline:none;background:var(--paper);color:var(--ink)">
            <button class="btn btn-primary btn-sm">Send</button>
          </div>
        </div>
      </div>`;
  },

  /* ── SETTINGS ── */
  settings() {
    return `
      <div class="page-header"><div><h1>Settings</h1><p>Manage your profile and preferences</p></div><button class="btn btn-primary">Save changes</button></div>
      <div class="settings-section">
        <h2>Profile</h2>
        <div class="form-row">
          <div class="form-group"><label>First name</label><input type="text" value="Sara"></div>
          <div class="form-group"><label>Last name</label><input type="text" value="Akram"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Email</label><input type="email" value="sara@example.com"></div>
          <div class="form-group"><label>Phone</label><input type="tel" value="+1 (204) 555-0123"></div>
        </div>
        <div class="form-group" style="margin-bottom:14px"><label>Bio</label><textarea rows="3">Biochemistry graduate passionate about making science accessible to all students.</textarea></div>
      </div>
      <div class="settings-section">
        <h2>Teaching</h2>
        <div class="form-row">
          <div class="form-group"><label>Subjects</label><input type="text" value="Biology, Chemistry, Math"></div>
          <div class="form-group"><label>Grade levels</label><input type="text" value="Grades 6–12"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Hourly rate ($)</label><input type="number" value="40"></div>
          <div class="form-group"><label>Session length</label><select><option>60 minutes</option><option>45 minutes</option><option>90 minutes</option></select></div>
        </div>
      </div>`;
  },
};
