/* ─── AI Resume Intelligence — Frontend Logic ─── */

const API = "";

/* ═══ DEMO DATA ═══ */
const DEMO_RESUME = `Vikas Kumar Singh — Full-Stack Developer & AI Builder

SKILLS
Python, PyTorch, scikit-learn, Hugging Face, transformers, NLP, deep learning, MLflow, FastAPI, React, TypeScript, PostgreSQL, Docker, AWS, Git, REST API

EXPERIENCE
AI Resume Intelligence Platform — Personal Project
• Built end-to-end ML pipeline: TF-IDF + Logistic Regression classifier for resume categorization
• Implemented semantic matching using cosine similarity for resume-JD alignment scoring
• Developed FastAPI backend with PDF parsing, skill extraction, and ATS scoring endpoints
• Created responsive frontend with real-time analysis visualization

REST APIs on AWS EC2 — Freelance
• Deployed containerized microservices on EC2 using Docker and CI/CD pipelines
• Built RESTful APIs serving 10k+ daily requests with <200ms latency

EDUCATION
B.Tech Computer Science Engineering — Dronacharya College of Engineering, Gurugram

INTERNSHIP
Technical Writing Intern — Hawksvale UK
• Authored developer documentation and API guides for internal tools`;

const DEMO_JOB = `AI/ML Engineer — TechCorp Inc.

ABOUT THE ROLE
We are looking for an AI/ML Engineer to join our growing team. You will design, build, and deploy machine learning models for production applications.

REQUIRED SKILLS
• Python (3+ years)
• PyTorch or TensorFlow
• NLP and text processing
• FastAPI or Flask for model serving
• AWS (EC2, S3, Lambda)
• Docker and containerization
• MLflow for experiment tracking
• Git and CI/CD

NICE TO HAVE
• Kubernetes and Terraform
• Apache Spark for large-scale processing
• Experience with LLMs and transformer architectures

REQUIREMENTS
• 1-3 years of hands-on ML engineering experience
• B.Tech/B.E. in Computer Science or related field
• Strong problem-solving and communication skills`;

/* ═══ LOAD DEMO FUNCTIONS ═══ */
function loadResumeDemo() {
  document.getElementById("resumeInput").value = DEMO_RESUME;
}
function loadJobDemo() {
  document.getElementById("jobInput").value = DEMO_JOB;
}
function clearResume() {
  document.getElementById("resumeInput").value = "";
  document.getElementById("resumeFile").value = "";
  document.getElementById("resumeFileName").textContent = "";
  const zone = document.getElementById("resumeDropZone");
  if (zone) zone.classList.remove("has-file");
}

function clearJob() {
  document.getElementById("jobInput").value = "";
  document.getElementById("jobFile").value = "";
  document.getElementById("jobFileName").textContent = "";
  const zone = document.getElementById("jobDropZone");
  if (zone) zone.classList.remove("has-file");
}

function clearAll() {
  clearResume();
  clearJob();
  document.getElementById("results").classList.remove("visible");
}

/* ═══ DRAG & DROP + FILE UPLOAD ═══ */
function setupUploadZone(zoneId, fileInputId, fileNameId, targetTextareaId) {
  const zone = document.getElementById(zoneId);
  const fileInput = document.getElementById(fileInputId);
  const fileNameEl = document.getElementById(fileNameId);
  const btn = zone.querySelector(".upload-btn");

  btn.addEventListener("click", (e) => { e.stopPropagation(); fileInput.click(); });
  zone.addEventListener("click", () => fileInput.click());

  ["dragenter", "dragover"].forEach(evt => {
    zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.add("drag-over"); });
  });
  ["dragleave", "drop"].forEach(evt => {
    zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.remove("drag-over"); });
  });

  zone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file, fileNameEl, zone, targetTextareaId);
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) handleFileUpload(file, fileNameEl, zone, targetTextareaId);
  });
}

async function handleFileUpload(file, fileNameEl, zone, targetTextareaId) {
  const formData = new FormData();
  formData.append("file", file);
  fileNameEl.textContent = "Uploading " + file.name + "...";
  zone.classList.add("has-file");

  try {
    const res = await fetch(API + "/api/v1/resume/upload", { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Upload failed");
    }
    const data = await res.json();
    document.getElementById(targetTextareaId).value = data.text_preview;
    fileNameEl.textContent = "✓ " + file.name + " (" + data.char_count + " chars)";
  } catch (e) {
    fileNameEl.textContent = "✗ " + e.message;
    zone.classList.remove("has-file");
    alert("Upload error: " + e.message);
  }
}

/* ═══ PROS / CONS GENERATORS ═══ */
function genPros(matched, extra, semPct, skillPct, cat) {
  const p = [];
  if (matched.length >= 5) p.push(`${matched.length} required skills matched — strong ATS keyword coverage.`);
  if (semPct >= 35) p.push(`Semantic relevance ${semPct}% — resume language aligns with JD context.`);
  if (skillPct >= 70) p.push(`Keyword density ${skillPct}% — likely to pass automated ATS filters.`);
  if (extra.length >= 3) p.push(`${extra.length} extra skills beyond requirements show technical breadth.`);
  if (cat === "AI/ML" || cat === "Data Science") p.push(`Role predicted as ${cat} — resume clearly signals the right domain.`);
  if (matched.includes("Docker") || matched.includes("AWS")) p.push("Cloud & containerization skills present — a key differentiator.");
  if (p.length === 0) p.push("Resume contains relevant experience aligned to the role.");
  return p.slice(0, 4);
}

function genCons(missing, semPct, skillPct, atsScore) {
  const c = [];
  if (missing.length > 0) {
    const extra = missing.length > 3 ? ` +${missing.length - 3} more` : "";
    c.push(`Missing ${missing.length} skill${missing.length > 1 ? "s" : ""}: ${missing.slice(0, 3).join(", ")}${extra}.`);
  }
  if (semPct < 25) c.push(`Semantic score ${semPct}% — resume phrasing doesn't mirror JD language.`);
  if (skillPct < 60) c.push(`Keyword density ${skillPct}% — below typical 60-70% ATS threshold.`);
  if (atsScore < 50) c.push("ATS score below 50 — significant rework needed before applying.");
  if (missing.includes("Kubernetes") || missing.includes("Terraform")) c.push("IaC skills (K8s/Terraform) absent — common hard requirement.");
  if (c.length < 2) c.push("Add quantified impact (e.g. 'reduced latency by 40%') to bullet points.");
  return c.slice(0, 4);
}

/* ═══ MAIN ANALYSIS ═══ */
async function runAnalysis() {
  const resume = document.getElementById("resumeInput").value.trim();
  const job = document.getElementById("jobInput").value.trim();
  if (!resume || !job) { alert("Please provide both a Resume and a Job Description."); return; }

  const loader = document.getElementById("loader");
  const results = document.getElementById("results");
  const btn = document.getElementById("analyzeBtn");

  loader.classList.add("visible");
  results.classList.remove("visible");
  btn.disabled = true;

  const steps = ["Sending to backend...", "Running classifier...", "Extracting skills...", "Computing cosine similarity...", "Generating ATS report..."];
  let si = 0;
  const iv = setInterval(() => { document.getElementById("loaderText").textContent = steps[si++ % steps.length]; }, 600);

  try {
    const res = await fetch(API + "/api/v1/resume/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resume, job_description: job }),
    });
    clearInterval(iv);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Backend error: ${res.status}`);
    }
    const data = await res.json();
    const clf = data.classification;
    const match = data.matching;
    const atsScore = match.match_score;
    const semPct = match.semantic_score;
    const skillPct = match.skill_score;
    const matched = match.matched_skills;
    const missing = match.missing_skills;
    const extra = match.resume_skills.filter(s => !matched.includes(s));

    // Save to history
    try {
      const history = JSON.parse(localStorage.getItem('resumeHistory') || '[]');
      history.unshift({
        id: Date.now(),
        date: new Date().toISOString(),
        score: atsScore,
        role: clf.category,
        skillsMatched: matched.length,
        skillsTotal: matched.length + missing.length
      });
      localStorage.setItem('resumeHistory', JSON.stringify(history.slice(0, 50)));
    } catch(e) { console.error("Failed to save history", e); }

    render({ clf, matched, missing, extra, jSkills: [...matched, ...missing], semPct, skillPct, atsScore });
    loader.classList.remove("visible");
    results.classList.add("visible");
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    clearInterval(iv);
    loader.classList.remove("visible");
    alert("Analysis failed: " + error.message + "\n\nMake sure backend is running:\nuvicorn backend.app.main:app --reload");
  } finally {
    btn.disabled = false;
  }
}

/* ═══ RENDER RESULTS ═══ */
function render({ clf, matched, missing, extra, jSkills, semPct, skillPct, atsScore }) {
  const C = 2 * Math.PI * 44;
  const ring = document.getElementById("atsRing");
  ring.style.strokeDashoffset = C * (1 - atsScore / 100);
  const col = atsScore >= 70 ? "#4ade80" : atsScore >= 45 ? "#fbbf24" : "#f87171";
  ring.style.stroke = col;
  document.getElementById("atsScore").textContent = atsScore;
  document.getElementById("atsScore").style.color = col;

  const vt = atsScore >= 70 ? "Strong Match" : atsScore >= 45 ? "Moderate Match" : "Weak Match";
  const vc = atsScore >= 70 ? "good" : atsScore >= 45 ? "warn" : "bad";
  const vChip = document.getElementById("verdictChip");
  vChip.textContent = vt;
  vChip.className = "verdict-chip " + vc;
  document.getElementById("heroTitle").textContent = "Predicted Role: " + clf.category;
  document.getElementById("heroSub").textContent = `Confidence ${(clf.confidence * 100).toFixed(1)}% · ${matched.length}/${jSkills.length} skills matched · TF-IDF+LR`;
  document.getElementById("verdictSub").textContent = `${(clf.confidence * 100).toFixed(0)}% confidence`;

  const metrics = [
    { label: "Skill Match", val: skillPct, color: skillPct >= 70 ? "#4ade80" : skillPct >= 45 ? "#fbbf24" : "#f87171" },
    { label: "Semantic Score", val: semPct, color: semPct >= 30 ? "#22d3ee" : "#f87171" },
    { label: "ATS Score", val: Math.round(atsScore), color: col },
  ];
  document.getElementById("metricsRow").innerHTML = metrics.map(m => `<div class="metric-card">
    <div class="mc-label">${m.label}</div>
    <div class="mc-val" style="color:${m.color}">${m.val}<span style="font-size:14px;color:var(--mute)">%</span></div>
    <div class="mc-bar"><div class="mc-bar-fill" style="width:${m.val}%;background:${m.color}"></div></div>
  </div>`).join("");

  const pros = genPros(matched, extra, semPct, skillPct, clf.category);
  const cons = genCons(missing, semPct, skillPct, atsScore);
  document.getElementById("prosList").innerHTML = pros.map(p => `<div class="pc-item"><div class="pc-dot"></div><span>${p}</span></div>`).join("");
  document.getElementById("consList").innerHTML = cons.map(c => `<div class="pc-item"><div class="pc-dot"></div><span>${c}</span></div>`).join("");

  const bars = [
    { name: "Skill Overlap", pct: skillPct, color: "#22d3ee" },
    { name: "Semantic Sim.", pct: semPct, color: "#a78bfa" },
    { name: "Keyword Cover", pct: Math.round((matched.length / Math.max(jSkills.length, 1)) * 100), color: "#4ade80" },
  ];
  document.getElementById("skillBars").innerHTML = bars.map(b => `<div class="skill-row">
    <div class="skill-name">${b.name}</div>
    <div class="skill-bar-wrap"><div class="skill-bar-fill" style="width:${b.pct}%;background:${b.color}"></div></div>
    <div class="skill-pct">${b.pct}%</div>
  </div>`).join("");

  document.getElementById("matchedChips").innerHTML = matched.map(s => `<span class="chip matched">${s}</span>`).join("");
  document.getElementById("missingChips").innerHTML = missing.map(s => `<span class="chip missing">${s}</span>`).join("");
  document.getElementById("extraChips").innerHTML = extra.map(s => `<span class="chip extra">${s}</span>`).join("");

  document.getElementById("mCategory").textContent = clf.category;
  document.getElementById("mConfidence").textContent = (clf.confidence * 100).toFixed(1) + "%";
  document.getElementById("mSemantic").textContent = semPct + "%";
  document.getElementById("mSkillScore").textContent = skillPct + "%";
  document.getElementById("mOverall").textContent = atsScore + "%";

  const sorted = Object.entries(clf.scores).sort((a, b) => b[1] - a[1]);
  document.getElementById("classProbs").innerHTML = sorted.map(([cat, prob]) => {
    const pct = Math.round(prob * 100);
    const active = cat === clf.category;
    return `<div class="skill-row" style="margin-bottom:7px">
      <div class="skill-name" style="${active ? "color:var(--primary);font-weight:700" : ""}">${cat}</div>
      <div class="skill-bar-wrap"><div class="skill-bar-fill" style="width:${pct}%;background:${active ? "var(--primary)" : "var(--secondary-bg)"}"></div></div>
      <div class="skill-pct" style="${active ? "color:var(--primary);font-weight:700" : ""}">${pct}%</div>
    </div>`;
  }).join("");

  const top3 = missing.slice(0, 3);
  let reco = "";
  if (atsScore >= 70) {
    reco = `<strong>Ready to apply.</strong> Score ${atsScore}% — strong alignment with the JD. `;
    if (top3.length) reco += `Adding ${top3.join(", ")} pushes this higher. `;
    reco += "Mirror the JD's exact phrasing in your summary for maximum ATS pass-through.";
  } else if (atsScore >= 45) {
    reco = `<strong>Apply with revisions.</strong> Score ${atsScore}% is below the typical 70% threshold. `;
    if (top3.length) reco += `Priority gaps: <strong>${top3.join(", ")}</strong>. `;
    reco += "Add these as projects or coursework. Use the JD's exact keywords.";
  } else {
    reco = `<strong>Significant rework needed.</strong> Score ${atsScore}% — likely below automated screening. `;
    if (top3.length) reco += `Critical missing: <strong>${top3.join(", ")}</strong>. `;
    reco += "Build 1-2 projects using these skills, then re-run analysis.";
  }
  document.getElementById("recoBox").innerHTML = reco;
}

/* ═══ INIT ═══ */
document.addEventListener("DOMContentLoaded", () => {
  // Setup upload zones
  if (document.getElementById("resumeDropZone")) {
    setupUploadZone("resumeDropZone", "resumeFile", "resumeFileName", "resumeInput");
  }
  if (document.getElementById("jobDropZone")) {
    setupUploadZone("jobDropZone", "jobFile", "jobFileName", "jobInput");
  }

});
