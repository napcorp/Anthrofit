/* ==========================================================================
   AnthroFit OS - Monochromatic Questionnaire & Virtual Cursor Engine
   ========================================================================== */

const appState = {
  currentTab: 'questionnaire', // 'questionnaire' | 'inventory' | 'analytics'
  wizardStep: 1, // 1: Select/Add Anchor, 2: Choose Target, 3: Answer & Verdict
  selectedAnchorId: 'REF-UNIQLO-AIRISM-M',
  selectedTargetId: 'TARGET-COS-BOXY-TEE',
  fitPreference: 'true_to_anchor',
  inventory: [],
  targets: [],
  verdictData: null,
  isDemoRunning: false
};

// Boot logic
document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  setupNav();
  setupDemoEngine();
  renderCurrentView();
});

async function loadData() {
  try {
    const [invRes, tgtRes] = await Promise.all([
      fetch('/api/inventory'),
      fetch('/api/targets')
    ]);
    appState.inventory = await invRes.json();
    appState.targets = await tgtRes.json();
  } catch (err) {
    console.error('Data load error:', err);
  }
}

function setupNav() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.currentTab = btn.getAttribute('data-tab');
      renderCurrentView();
    });
  });

  const demoBtn = document.getElementById('toggleDemoBtn');
  if (demoBtn) {
    demoBtn.addEventListener('click', toggleDemoTour);
  }
}

function renderCurrentView() {
  const container = document.getElementById('viewContainer');
  if (!container) return;

  if (appState.currentTab === 'questionnaire') {
    container.innerHTML = renderQuestionnaire();
    attachQuestionnaireEvents();
  } else if (appState.currentTab === 'inventory') {
    container.innerHTML = renderInventoryCloset();
    attachInventoryEvents();
  } else if (appState.currentTab === 'analytics') {
    container.innerHTML = renderAnalytics();
  }
}

/* ==========================================================================
   VIEW 1: QUESTIONNAIRE FLOW (Step 1 -> Step 2 -> Step 3 Verdict)
   ========================================================================== */

function renderQuestionnaire() {
  const currentTarget = appState.targets.find(t => t.id === appState.selectedTargetId) || appState.targets[0];
  const matchingAnchors = appState.inventory.filter(a => a.category === currentTarget.category);
  const selectedAnchor = appState.inventory.find(a => a.id === appState.selectedAnchorId) || matchingAnchors[0] || appState.inventory[0];

  return `
    <div class="editorial-hero">
      <span class="editorial-tagline">Differential Garment Translation</span>
      <h1 class="editorial-title">Fit Questionnaire</h1>
      <p class="editorial-lead">
        Select a piece you already own that fits you perfectly. We compute the exact cutting tolerance differential to tell you which size to purchase.
      </p>
    </div>

    <!-- 3-Step Wizard Navigation -->
    <div class="wizard-stepper">
      <div class="step-indicator ${appState.wizardStep >= 1 ? 'active' : ''} ${appState.wizardStep > 1 ? 'completed' : ''}" id="step1Indicator">
        <span class="step-num">1</span>
        <span>Your Reference Piece</span>
      </div>
      <div class="step-divider"></div>
      <div class="step-indicator ${appState.wizardStep >= 2 ? 'active' : ''} ${appState.wizardStep > 2 ? 'completed' : ''}" id="step2Indicator">
        <span class="step-num">2</span>
        <span>Target Piece</span>
      </div>
      <div class="step-divider"></div>
      <div class="step-indicator ${appState.wizardStep >= 3 ? 'active' : ''}" id="step3Indicator">
        <span class="step-num">3</span>
        <span>Size Recommendation</span>
      </div>
    </div>

    <!-- Step 1: Select from your wardrobe -->
    ${appState.wizardStep === 1 ? `
      <div class="card" id="step1Card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <div>
            <h3 style="font-size: 1.25rem; font-weight: 700;">Step 1: Which garment in your wardrobe fits you best?</h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;">
              Choose an anchor from your saved wardrobe. Clothes you own already contain the precise volume tolerances of your body.
            </p>
          </div>
          <button class="btn-secondary" id="quickAddInventoryBtn" style="font-size: 0.75rem; padding: 0.4rem 0.85rem;">
            + Add New Garment
          </button>
        </div>

        <div class="closet-grid">
          ${appState.inventory.map(item => `
            <div class="closet-item-card ${item.id === appState.selectedAnchorId ? 'selected' : ''}" data-anchor-id="${item.id}" id="anchor-${item.id}">
              <div>
                <div class="closet-card-top">
                  <span class="brand-badge-pill">${item.brand}</span>
                  <span class="size-tag-display">Size ${item.tag_size}</span>
                </div>
                <div class="closet-item-name">${item.model_name}</div>
                <div class="closet-item-sub">${item.composition} · ${item.category.toUpperCase()}</div>
              </div>
              <div style="margin-top: 0.75rem; font-size: 0.7rem; color: var(--text-tertiary); font-family: var(--font-mono);">
                FABRIC: ${item.stretch}
              </div>
            </div>
          `).join('')}
        </div>

        <div style="margin-top: 1.5rem; display: flex; justify-content: flex-end;">
          <button class="btn-primary" id="goToStep2Btn" style="width: auto; padding: 0.75rem 2rem;">
            Continue to Target Item →
          </button>
        </div>
      </div>
    ` : ''}

    <!-- Step 2: What are you looking to buy? -->
    ${appState.wizardStep === 2 ? `
      <div class="card" id="step2Card">
        <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">Step 2: What garment do you want to buy?</h3>
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
          Select the item you are considering. We compare its manufacturing tech pack against your reference: <strong style="color: var(--text-primary);">${selectedAnchor.display_name}</strong>.
        </p>

        <div style="display: flex; gap: 0.75rem; margin-bottom: 1.5rem; overflow-x: auto; padding-bottom: 4px;">
          ${appState.targets.map(t => `
            <button class="btn-secondary ${t.id === appState.selectedTargetId ? 'btn-primary' : ''}" data-target-id="${t.id}" id="targetBtn-${t.id}" style="font-size: 0.8rem; white-space: nowrap;">
              ${t.brand} · ${t.name.split(' ')[0]}
            </button>
          `).join('')}
        </div>

        <div class="target-product-card">
          <div class="target-garment-illustration">
            ${renderGarmentVector(currentTarget.category)}
            <div style="position: absolute; bottom: 8px; font-size: 0.65rem; color: var(--text-tertiary); font-family: var(--font-mono);">
              CAD PATTERN SPEC: ${currentTarget.id}
            </div>
          </div>

          <div class="target-info-pane">
            <div>
              <span class="target-brand-eyebrow">${currentTarget.brand}</span>
              <h2 class="target-item-title">${currentTarget.name}</h2>
              <div class="target-item-price">$${currentTarget.price.toFixed(2)} USD</div>
            </div>

            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">
              ${currentTarget.desc}
            </p>

            <div style="font-size: 0.8rem; background: var(--bg-subtle); padding: 0.75rem; border-radius: var(--radius-md);">
              <span style="font-weight: 700; color: var(--text-primary);">Fabric & Drape:</span>
              <div style="color: var(--text-secondary); margin-top: 2px;">${currentTarget.fabric}</div>
            </div>

            <div>
              <label style="font-size: 0.8rem; font-weight: 700; color: var(--text-primary);">How do you prefer this piece to drape?</label>
              <div class="pref-selector">
                <div class="pref-chip ${appState.fitPreference === 'fitted' ? 'selected' : ''}" data-pref="fitted" id="prefFitted">Fitted / Sharp</div>
                <div class="pref-chip ${appState.fitPreference === 'true_to_anchor' ? 'selected' : ''}" data-pref="true_to_anchor" id="prefTrue">True to Anchor</div>
                <div class="pref-chip ${appState.fitPreference === 'relaxed' ? 'selected' : ''}" data-pref="relaxed" id="prefRelaxed">Relaxed / Boxy</div>
              </div>
            </div>

            <div style="display: flex; gap: 0.75rem; margin-top: 0.5rem;">
              <button class="btn-secondary" id="backToStep1Btn" style="flex: 1;">
                ← Change Anchor
              </button>
              <button class="btn-primary" id="calculateSizeBtn" style="flex: 2;">
                Calculate What Size to Get →
              </button>
            </div>
          </div>
        </div>
      </div>
    ` : ''}

    <!-- Step 3: Verified Answer & Tactile Breakdown -->
    ${appState.wizardStep === 3 && appState.verdictData ? `
      <div class="verification-verdict-card" id="step3Card">
        <div class="verdict-header-row">
          <div>
            <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary);">
              Differential Vector Verification
            </span>
            <h2 style="font-size: 1.7rem; font-weight: 800; letter-spacing: -0.03em; margin-top: 2px;">
              Your Recommended Size
            </h2>
          </div>
          <div class="verdict-confidence-badge" id="confidenceBadge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span>${appState.verdictData.fit_confidence_pct}% Match Confidence</span>
          </div>
        </div>

        <div class="verdict-answer-box">
          <div style="font-size: 0.85rem; color: var(--text-secondary);">
            Matched against your: <strong style="color: var(--text-primary);">${appState.verdictData.anchor_used}</strong>
          </div>
          <div class="verdict-main-callout">
            You should purchase this in <span class="verdict-exact-size" id="recommendedSizeTag">Size ${appState.verdictData.recommended_size}</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 2px;">
            ${appState.verdictData.verdict_summary}
          </p>
        </div>

        <!-- Tactile Friction Breakdown -->
        <div>
          <h4 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 0.75rem;">Tactile Variance Points (How it will feel on your body):</h4>
          <div class="friction-breakdown">
            ${appState.verdictData.friction_points.map(fp => `
              <div class="friction-point-item">
                <div>
                  <div class="friction-zone">${fp.zone} · <span style="font-weight: 500; color: var(--text-secondary);">${fp.assessment}</span></div>
                  <div class="friction-note">${fp.note}</div>
                </div>
                <div class="friction-metric">${fp.delta}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <div style="margin-top: 1.5rem; padding: 0.85rem 1rem; background: var(--bg-subtle); border-radius: var(--radius-md); display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
          <span style="color: var(--text-secondary);">Estimated Return Risk:</span>
          <span style="font-family: var(--font-mono); font-weight: 700; color: var(--text-primary);">${appState.verdictData.return_risk_pct}% (Industry avg: 32%)</span>
        </div>

        <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem;">
          <button class="btn-secondary" id="restartQuestionnaireBtn" style="flex: 1;">
            ← Run Another Comparison
          </button>
          <button class="btn-primary" id="confirmCheckoutBtn" style="flex: 2;">
            Select Size ${appState.verdictData.recommended_size} & Proceed
          </button>
        </div>
      </div>
    ` : ''}
  `;
}

function attachQuestionnaireEvents() {
  // Step 1 Events
  document.querySelectorAll('.closet-item-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.closet-item-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      appState.selectedAnchorId = card.getAttribute('data-anchor-id');
    });
  });

  const goToStep2Btn = document.getElementById('goToStep2Btn');
  if (goToStep2Btn) {
    goToStep2Btn.addEventListener('click', () => {
      appState.wizardStep = 2;
      renderCurrentView();
    });
  }

  const quickAddBtn = document.getElementById('quickAddInventoryBtn');
  if (quickAddBtn) {
    quickAddBtn.addEventListener('click', () => {
      appState.currentTab = 'inventory';
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      const invTab = document.querySelector('[data-tab="inventory"]');
      if (invTab) invTab.classList.add('active');
      renderCurrentView();
    });
  }

  // Step 2 Events
  document.querySelectorAll('[id^="targetBtn-"]').forEach(btn => {
    btn.addEventListener('click', () => {
      appState.selectedTargetId = btn.getAttribute('data-target-id');
      renderCurrentView();
    });
  });

  document.querySelectorAll('.pref-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.pref-chip').forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      appState.fitPreference = chip.getAttribute('data-pref');
    });
  });

  const backToStep1Btn = document.getElementById('backToStep1Btn');
  if (backToStep1Btn) {
    backToStep1Btn.addEventListener('click', () => {
      appState.wizardStep = 1;
      renderCurrentView();
    });
  }

  const calculateSizeBtn = document.getElementById('calculateSizeBtn');
  if (calculateSizeBtn) {
    calculateSizeBtn.addEventListener('click', async () => {
      calculateSizeBtn.innerText = 'Calculating Vector Differential...';
      try {
        const res = await fetch('/api/questionnaire/resolve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            selected_anchor_id: appState.selectedAnchorId,
            target_product_id: appState.selectedTargetId,
            fit_preference: appState.fitPreference
          })
        });
        if (res.ok) {
          appState.verdictData = await res.json();
          appState.wizardStep = 3;
          renderCurrentView();
        }
      } catch (err) {
        console.error('Calculation error:', err);
      }
    });
  }

  // Step 3 Events
  const restartBtn = document.getElementById('restartQuestionnaireBtn');
  if (restartBtn) {
    restartBtn.addEventListener('click', () => {
      appState.wizardStep = 1;
      appState.verdictData = null;
      renderCurrentView();
    });
  }
}

/* ==========================================================================
   VIEW 2: INVENTORY / CLOSET MANAGER
   ========================================================================== */

function renderInventoryCloset() {
  return `
    <div class="editorial-hero">
      <span class="editorial-tagline">Personal Wardrobe Knowledge Base</span>
      <h1 class="editorial-title">Your Size Anchors</h1>
      <p class="editorial-lead">
        Register garments you already own that fit comfortably. You never have to measure your waist or chest again.
      </p>
    </div>

    <div class="card">
      <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 0.25rem;">Add a Garment You Love</h3>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
        Input the label brand, model, and tag size. AnthroFit references manufacturing CAD specs automatically.
      </p>

      <form id="addInventoryForm" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div>
          <label style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Brand</label>
          <input type="text" id="invBrand" required placeholder="e.g. Uniqlo, Nike, Levi's" 
                 style="width: 100%; padding: 0.65rem; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-top: 4px; font-family: var(--font-sans);">
        </div>
        <div>
          <label style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Model / Item Name</label>
          <input type="text" id="invModel" required placeholder="e.g. Airism Cotton Crew, 511 Slim" 
                 style="width: 100%; padding: 0.65rem; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-top: 4px; font-family: var(--font-sans);">
        </div>
        <div>
          <label style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Tag Size</label>
          <input type="text" id="invSize" required placeholder="e.g. M, L, 32x32" 
                 style="width: 100%; padding: 0.65rem; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-top: 4px; font-family: var(--font-sans);">
        </div>
        <div>
          <label style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Category</label>
          <select id="invCategory" style="width: 100%; padding: 0.65rem; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-top: 4px; font-family: var(--font-sans); background: #fff;">
            <option value="tops">Tops / Shirts / Outerwear</option>
            <option value="bottoms">Bottoms / Denim / Trousers</option>
          </select>
        </div>
        <div style="grid-column: span 2; margin-top: 0.5rem;">
          <button type="submit" class="btn-primary" id="saveInventoryBtn">
            + Save to My Sizing Anchors
          </button>
        </div>
      </form>
    </div>

    <div style="margin-top: 2rem;">
      <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 0.75rem;">Your Saved Anchors (${appState.inventory.length})</h3>
      <div class="closet-grid">
        ${appState.inventory.map(item => `
          <div class="closet-item-card">
            <div>
              <div class="closet-card-top">
                <span class="brand-badge-pill">${item.brand}</span>
                <span class="size-tag-display">Size ${item.tag_size}</span>
              </div>
              <div class="closet-item-name">${item.model_name}</div>
              <div class="closet-item-sub">${item.composition || '100% Cotton'} · ${item.category.toUpperCase()}</div>
            </div>
            <div style="margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.7rem; color: var(--text-tertiary); font-family: var(--font-mono);">${item.id}</span>
              <button class="btn-secondary" style="font-size: 0.7rem; padding: 2px 8px;" onclick="useAsAnchor('${item.id}')">Use in Questionnaire</button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function attachInventoryEvents() {
  const form = document.getElementById('addInventoryForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const brand = document.getElementById('invBrand').value;
      const model = document.getElementById('invModel').value;
      const size = document.getElementById('invSize').value;
      const cat = document.getElementById('invCategory').value;

      try {
        const res = await fetch('/api/inventory/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            brand: brand,
            model_name: model,
            tag_size: size,
            category: cat
          })
        });
        if (res.ok) {
          const result = await res.json();
          appState.inventory.unshift(result.item);
          appState.selectedAnchorId = result.item.id;
          renderCurrentView();
        }
      } catch (err) {
        console.error('Save inventory error:', err);
      }
    });
  }
}

window.useAsAnchor = function(id) {
  appState.selectedAnchorId = id;
  appState.currentTab = 'questionnaire';
  appState.wizardStep = 2;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const qTab = document.querySelector('[data-tab="questionnaire"]');
  if (qTab) qTab.classList.add('active');
  renderCurrentView();
};

/* ==========================================================================
   VIEW 3: ENTERPRISE ANALYTICS
   ========================================================================== */

function renderAnalytics() {
  return `
    <div class="editorial-hero">
      <span class="editorial-tagline">Enterprise Return Reduction</span>
      <h1 class="editorial-title">Platform Impact</h1>
      <p class="editorial-lead">
        Aggregated reverse logistics margin recovery across connected retailer checkout integrations.
      </p>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
      <div class="card" style="margin-bottom: 0;">
        <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Return Rate</span>
        <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0.25rem 0;">3.8%</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">-87.9% vs 31.4% industry baseline</div>
      </div>
      <div class="card" style="margin-bottom: 0;">
        <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Margin Saved</span>
        <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0.25rem 0;">$1.48M</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">Per 100,000 orders processed</div>
      </div>
      <div class="card" style="margin-bottom: 0;">
        <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Conversion Lift</span>
        <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0.25rem 0;">+19.4%</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">Eliminated sizing hesitation</div>
      </div>
      <div class="card" style="margin-bottom: 0;">
        <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Landfill Diverted</span>
        <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0.25rem 0;">18,450 kg</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">268 metric tons CO₂e averted</div>
      </div>
    </div>
  `;
}

// Clean Monochrome Garment Vector Visualizer
function renderGarmentVector(category) {
  if (category === 'tops') {
    return `
      <svg width="180" height="220" viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M60 20 Q100 42 140 20 L180 50 L165 90 L140 80 L140 210 L60 210 L60 80 L35 90 L20 50 Z" 
              stroke="#09090b" stroke-width="2.5" fill="#ffffff" />
        <path d="M75 25 C85 45 115 45 125 25" stroke="#09090b" stroke-width="2" fill="none" />
        <line x1="60" y1="95" x2="140" y2="95" stroke="#71717a" stroke-width="1.5" stroke-dasharray="3 3" />
        <text x="100" y="90" fill="#09090b" font-size="9" font-family="monospace" text-anchor="middle">CHEST ANCHOR</text>
      </svg>
    `;
  } else {
    return `
      <svg width="180" height="220" viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M60 20 L140 20 L145 70 L135 220 L110 220 L100 95 L90 220 L65 220 L55 70 Z" 
              stroke="#09090b" stroke-width="2.5" fill="#ffffff" />
        <line x1="60" y1="20" x2="140" y2="20" stroke="#09090b" stroke-width="3.5" />
        <line x1="58" y1="85" x2="100" y2="85" stroke="#71717a" stroke-width="1.5" stroke-dasharray="3 3" />
        <text x="79" y="80" fill="#09090b" font-size="9" font-family="monospace" text-anchor="middle">THIGH ANCHOR</text>
      </svg>
    `;
  }
}

/* ==========================================================================
   VIRTUAL DEMO TOUR ENGINE (Autonomous Guided Walkthrough with Visible Cursor)
   ========================================================================== */

let demoInterval = null;

function setupDemoEngine() {
  if (!document.getElementById('virtualCursor')) {
    const cursor = document.createElement('div');
    cursor.id = 'virtualCursor';
    cursor.innerHTML = `
      <svg class="cursor-arrow-svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M4 3L11 20L14 13L21 10L4 3Z" fill="#000000" stroke="#ffffff" stroke-width="2"/>
      </svg>
      <div class="cursor-trail-pulse"></div>
    `;
    document.body.appendChild(cursor);
  }
}

async function moveCursorTo(selector, offsetX = 10, offsetY = 10) {
  const el = document.querySelector(selector);
  const cursor = document.getElementById('virtualCursor');
  if (!el || !cursor) return false;

  const rect = el.getBoundingClientRect();
  const targetX = rect.left + rect.width / 2 + offsetX;
  const targetY = rect.top + rect.height / 2 + offsetY;

  cursor.style.display = 'block';
  cursor.style.transform = `translate(${targetX}px, ${targetY}px)`;
  await delay(800);
  return el;
}

async function simulateClick(el) {
  const cursor = document.getElementById('virtualCursor');
  if (cursor) cursor.classList.add('cursor-clicking');
  await delay(200);
  if (el) el.click();
  await delay(300);
  if (cursor) cursor.classList.remove('cursor-clicking');
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function showDemoBanner(text) {
  let banner = document.getElementById('demoBanner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'demoBanner';
    banner.className = 'demo-banner';
    document.body.appendChild(banner);
  }
  banner.innerHTML = `
    <span style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block;"></span>
    <span class="demo-step-text">${text}</span>
    <button class="demo-stop-btn" onclick="stopDemoTour()">Stop Demo</button>
  `;
}

function hideDemoBanner() {
  const banner = document.getElementById('demoBanner');
  if (banner) banner.remove();
  const cursor = document.getElementById('virtualCursor');
  if (cursor) cursor.style.display = 'none';
}

window.stopDemoTour = function() {
  appState.isDemoRunning = false;
  hideDemoBanner();
  const demoBtn = document.getElementById('toggleDemoBtn');
  if (demoBtn) {
    demoBtn.classList.remove('active');
    demoBtn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      <span>Interactive Guided Demo</span>
    `;
  }
};

async function toggleDemoTour() {
  if (appState.isDemoRunning) {
    stopDemoTour();
    return;
  }

  appState.isDemoRunning = true;
  const demoBtn = document.getElementById('toggleDemoBtn');
  if (demoBtn) {
    demoBtn.classList.add('active');
    demoBtn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect width="14" height="14" x="5" y="5" rx="2"/></svg>
      <span>Stop Demo Tour</span>
    `;
  }

  // --- Step 1: Open Questionnaire ---
  showDemoBanner("Step 1: Navigating to Fit Questionnaire...");
  appState.currentTab = 'questionnaire';
  appState.wizardStep = 1;
  renderCurrentView();
  await delay(800);

  // --- Step 2: Select Uniqlo Airism Size M ---
  showDemoBanner("Selecting user's benchmark garment (Uniqlo Airism Tee - Size M)...");
  const anchorCard = await moveCursorTo('#anchor-REF-UNIQLO-AIRISM-M');
  if (anchorCard) await simulateClick(anchorCard);
  await delay(1000);

  // --- Step 3: Advance to Step 2 ---
  showDemoBanner("Submitting anchor to compare against target retailer tech packs...");
  const nextBtn = await moveCursorTo('#goToStep2Btn');
  if (nextBtn) await simulateClick(nextBtn);
  await delay(1200);

  // --- Step 4: Pick COS Clean-Cut Tee ---
  showDemoBanner("Browsing target garment: COS Heavyweight Clean-Cut Tee...");
  const targetBtn = await moveCursorTo('#targetBtn-TARGET-COS-BOXY-TEE');
  if (targetBtn) await simulateClick(targetBtn);
  await delay(1000);

  // --- Step 5: Toggle Drape Preference to True to Anchor ---
  showDemoBanner("Configuring fit preference: 'True to Anchor' drape...");
  const prefBtn = await moveCursorTo('#prefTrue');
  if (prefBtn) await simulateClick(prefBtn);
  await delay(1000);

  // --- Step 6: Click Calculate Size ---
  showDemoBanner("Running Differential Vector Math across 8 anatomical points...");
  const calcBtn = await moveCursorTo('#calculateSizeBtn');
  if (calcBtn) await simulateClick(calcBtn);
  await delay(1500);

  // --- Step 7: Inspect Verdict & Tactile Breakdowns ---
  showDemoBanner("Match Found: Size M (98% Confidence). Zero returns predicted!");
  await moveCursorTo('#recommendedSizeTag');
  await delay(2000);

  // --- Step 8: Visit Inventory Manager ---
  showDemoBanner("Touring the Inventory Manager to show custom garment input...");
  const invTab = await moveCursorTo('[data-tab="inventory"]');
  if (invTab) await simulateClick(invTab);
  await delay(2000);

  showDemoBanner("Demo walkthrough complete! You can explore freely now.");
  await delay(2500);
  stopDemoTour();
}
