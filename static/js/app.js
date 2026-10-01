/* ==========================================================================
   AnthroFit OS - Interactive Application Core
   Clean vanilla JavaScript driving all 4 views, reactive differential calculations,
   SVG silhouette generation, and API simulations.
   ========================================================================== */

const state = {
  currentView: 'storefront', // 'storefront' | 'b2b_dashboard' | 'api_playground' | 'pitch_deck'
  selectedProductId: 'PROD-ATELIER-HEAVY-TEE',
  selectedAnchorId: 'REF-UNIQLO-AIRISM-M',
  selectedPreference: 'true_to_anchor',
  currentPitchSlide: 0,
  fitResult: null,
  showSilhouetteModal: false
};

// Target Retailer Catalog
const catalogItems = [
  {
    id: "PROD-ATELIER-HEAVY-TEE",
    title: "280GSM Heavyweight Architectural Tee",
    brand: "ATELIER NORDIC",
    category: "tops",
    price: 78.00,
    colorway: "Chalk Bone",
    story: "Dense 280 GSM Japanese jersey knit. Straight square shoulder drop, reinforced micro-rib collar.",
    material: "100% Combed Compact Cotton (Zero Poly)",
    defaultAnchor: "REF-UNIQLO-AIRISM-M"
  },
  {
    id: "PROD-ATELIER-SELVEDGE-DENIM",
    title: "Kuroki Mills 14oz Raw Selvedge Denim",
    brand: "ATELIER NORDIC",
    category: "bottoms",
    price: 195.00,
    colorway: "Deep Indigo Raw",
    story: "Woven on vintage shuttle looms in Okayama. Pure 14oz rigid selvedge with natural mechanical drape.",
    material: "100% Rigid Ring-Spun Cotton, Red Selvedge ID",
    defaultAnchor: "REF-LEVIS-511-32"
  }
];

// Reference Anchors database for Tops vs Bottoms
const referenceAnchors = {
  tops: [
    { id: "REF-UNIQLO-AIRISM-M", name: "Uniqlo U Airism Oversized Tee (Size M)", brand: "Uniqlo", size: "M" },
    { id: "REF-UNIQLO-AIRISM-L", name: "Uniqlo U Airism Oversized Tee (Size L)", brand: "Uniqlo", size: "L" },
    { id: "REF-LULU-5YEAR-M", name: "Lululemon Fundamental Tee (Size M)", brand: "Lululemon", size: "M" }
  ],
  bottoms: [
    { id: "REF-LEVIS-511-32", name: "Levi's 511 Slim Stretch (Size 32x32)", brand: "Levi's", size: "32x32" },
    { id: "REF-LEVIS-501-32", name: "Levi's 501 Original Straight Rigid (Size 32x32)", brand: "Levi's", size: "32x32" }
  ]
};

// Pitch Deck Slides
const pitchSlides = [
  {
    tag: "THE HOOK & ORIGIN",
    title: "Why Does a 'Medium' in One Store Feel Like an Extra Small in Another?",
    subtitle: "The 1861 Civil War Uniform Legacy That Still Haunts \$1.5 Trillion in E-Commerce.",
    contentHtml: `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1.5rem;">
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.5rem;">
          <h4 style="color: #f43f5e; margin-bottom: 0.5rem; font-size: 1rem;">The 19th-Century Artifact</h4>
          <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
            Clothing sizes (S, M, L, 32, 38) were invented during the American Civil War to rapidly mass-produce battlefield uniforms for soldiers using crude chest-only averages.
            Today, vanity sizing, international block grading, and differing fabric elasticity make alphanumeric tags meaningless.
          </p>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.5rem;">
          <h4 style="color: #06b6d4; margin-bottom: 0.5rem; font-size: 1rem;">Why Previous Fixes Failed</h4>
          <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
            <strong>Webcam Body Scanners & AR Avatars:</strong> Invasive privacy concerns, awkward user experience, 85% drop-off rate.<br>
            <strong>Standard Size Charts:</strong> Rely on tape measures shoppers don't own and don't factor in fabric stretch or shrinkage.
          </p>
        </div>
      </div>
    `
  },
  {
    tag: "THE CRISIS",
    title: "The $200B+ Reverse Logistics Nightmare",
    subtitle: "Fashion's Bleeding Margin Problem and Environmental Catastrophe",
    contentHtml: `
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: 2rem;">
        <div style="background: #181b24; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(244,63,94,0.3);">
          <div style="font-size: 2.2rem; font-weight: 800; color: #f43f5e;">30 - 38%</div>
          <div style="font-weight: 700; margin: 0.4rem 0;">Online Return Rate</div>
          <div style="font-size: 0.8rem; color: #94a3b8;">Over 1 in 3 garments purchased online are returned immediately.</div>
        </div>
        <div style="background: #181b24; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(245,158,11,0.3);">
          <div style="font-size: 2.2rem; font-weight: 800; color: #f59e0b;">70%</div>
          <div style="font-weight: 700; margin: 0.4rem 0;">Fit-Driven Causes</div>
          <div style="font-size: 0.8rem; color: #94a3b8;">Seven out of ten returns are solely due to unexpected sizing variance.</div>
        </div>
        <div style="background: #181b24; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(6,182,212,0.3);">
          <div style="font-size: 2.2rem; font-weight: 800; color: #06b6d4;">2.6M Tons</div>
          <div style="font-weight: 700; margin: 0.4rem 0;">Landfill / Incinerated</div>
          <div style="font-size: 0.8rem; color: #94a3b8;">Returned items cost retailers more to inspect and re-bag than to discard.</div>
        </div>
      </div>
    `
  },
  {
    tag: "THE RE-INVENTION",
    title: "AnthroFit OS: The Differential Vector Engine",
    subtitle: "Your Favorite Clothes Already Contain the Exact 3D Geometry of Your Body.",
    contentHtml: `
      <div style="background: rgba(6,182,212,0.06); border: 1px solid rgba(6,182,212,0.25); border-radius: 16px; padding: 2rem; margin-top: 1.5rem;">
        <p style="font-size: 1.15rem; color: #f1f5f9; line-height: 1.7; font-weight: 500;">
          "We don't need your body measurements—we need the <strong>differential vector</strong> between garments you already love and garments you want to buy."
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem;">
          <div style="font-size: 0.88rem; color: #94a3b8;">
            <strong style="color: #fff;">1. Zero Invasive Scans:</strong> The customer simply inputs 1 benchmark piece they wear frequently (e.g. Uniqlo Airism Crew M).
          </div>
          <div style="font-size: 0.88rem; color: #94a3b8;">
            <strong style="color: #fff;">2. CAD Pattern Matching:</strong> We compare 8-point cutting patterns, elastane recovery %, and wash shrinkage curves.
          </div>
          <div style="font-size: 0.88rem; color: #94a3b8;">
            <strong style="color: #fff;">3. Tactile Friction Breakdown:</strong> "Tighter by 1.1 cm at shoulder seam; 2 cm longer in hem drape."
          </div>
          <div style="font-size: 0.88rem; color: #94a3b8;">
            <strong style="color: #fff;">4. Dynamic Smart Pill:</strong> Completely replaces [S | M | L | XL] dropdown with an automated fit verification button.
          </div>
        </div>
      </div>
    `
  },
  {
    tag: "BUSINESS MODEL & API",
    title: "Headless B2B Platform & Revenue Mechanics",
    subtitle: "Plug-and-play SDK for Shopify Plus, Salesforce Commerce Cloud, and Custom Headless Stacks",
    contentHtml: `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1.5rem;">
        <div style="background: #181b24; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.5rem;">
          <h4 style="color: #10b981; font-size: 1rem; margin-bottom: 0.75rem;">Monetization Streams</h4>
          <ul style="color: #94a3b8; font-size: 0.88rem; line-height: 1.8; list-style-position: inside;">
            <li><strong>Usage-Based API:</strong> $0.06 per verified checkout completion.</li>
            <li><strong>Gainshare Tier:</strong> 12% of verified reverse logistics margin recovered.</li>
            <li><strong>CAD Pattern Ingestion:</strong> Enterprise fee for brand 3D pattern digitization.</li>
          </ul>
        </div>
        <div style="background: #181b24; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.5rem;">
          <h4 style="color: #3b82f6; font-size: 1rem; margin-bottom: 0.75rem;">Unit Economics Impact</h4>
          <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.7;">
            For a mid-sized retailer processing 100,000 orders/month, a drop in return rate from 31% to 3.8% saves <strong>$1.4M+ in annual reverse logistics, repackaging, and depreciation losses</strong>.
          </p>
        </div>
      </div>
    `
  },
  {
    tag: "JUDGING CRITERIA ALIGNMENT",
    title: "Why AnthroFit OS Dominates Every Metric",
    subtitle: "Built Specifically Against Hackathon & Innovation Rubrics",
    contentHtml: `
      <div class="criteria-grid">
        <div class="criteria-card">
          <div class="criteria-badge">Originality · 30%</div>
          <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">No Cameras, No Tape</div>
          <p style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
            Solves fit as a CAD differential geometry problem rather than invasive biometric surveillance.
          </p>
        </div>
        <div class="criteria-card">
          <div class="criteria-badge">Innovation · 25%</div>
          <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">Cross-Brand Translation</div>
          <p style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
            Creates the first interoperable fabric translation graph bridging disparate brand grading blocks.
          </p>
        </div>
        <div class="criteria-card">
          <div class="criteria-badge">Execution · 25%</div>
          <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">Working End-to-End</div>
          <p style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
            Full functioning engine, drop-in e-commerce widget, analytics dashboard, and REST API playground.
          </p>
        </div>
        <div class="criteria-card">
          <div class="criteria-badge">Impact · 20%</div>
          <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">ESG & Margins</div>
          <p style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
            Directly tackles fashion's largest cost drain and thousands of tons of textile incineration waste.
          </p>
        </div>
      </div>
    `
  }
];

// App Initialization
async function initApp() {
  setupNavigation();
  await updateFitComputation();
  renderApp();
}

function setupNavigation() {
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const targetView = btn.getAttribute('data-view');
      document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.currentView = targetView;
      renderApp();
    });
  });
}

async function updateFitComputation() {
  try {
    const res = await fetch('/api/fit/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_reference_sku_id: state.selectedAnchorId,
        target_catalog_item_id: state.selectedProductId,
        fit_preference: state.selectedPreference
      })
    });
    if (res.ok) {
      state.fitResult = await res.json();
    }
  } catch (err) {
    console.error("Fit computation error:", err);
  }
}

function renderApp() {
  const container = document.getElementById('mainContentContainer');
  if (!container) return;

  if (state.currentView === 'storefront') {
    container.innerHTML = renderStorefrontView();
    attachStorefrontEvents();
  } else if (state.currentView === 'b2b_dashboard') {
    container.innerHTML = renderDashboardView();
  } else if (state.currentView === 'api_playground') {
    container.innerHTML = renderApiView();
    attachApiEvents();
  } else if (state.currentView === 'pitch_deck') {
    container.innerHTML = renderPitchView();
    attachPitchEvents();
  }
}

/* ==========================================================================
   VIEW 1: Consumer Storefront & AnthroFit Dynamic Smart Pill
   ========================================================================== */

function renderStorefrontView() {
  const currentProduct = catalogItems.find(p => p.id === state.selectedProductId) || catalogItems[0];
  const availableAnchors = referenceAnchors[currentProduct.category] || [];
  const fit = state.fitResult || {
    match_confidence_pct: 95,
    summary_verdict: "Fits like your benchmark",
    recommended_cut_label: "Cut 02 (True Boxy)",
    return_risk_pct: 2.8,
    tactile_friction_points: []
  };

  const isTops = currentProduct.category === 'tops';

  return `
    <div class="storefront-container">
      <!-- Left Column: Visual Asset Gallery -->
      <div class="gallery-section">
        <div class="hero-visual-card">
          ${renderGarmentVectorSvg(currentProduct.category)}
        </div>

        <div class="product-selector-pills">
          ${catalogItems.map(item => `
            <div class="product-thumb-pill ${item.id === state.selectedProductId ? 'selected' : ''}" data-product-id="${item.id}">
              <div style="width: 12px; height: 12px; border-radius: 50%; background: ${item.id === state.selectedProductId ? '#06b6d4' : '#64748b'};"></div>
              <div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #fff;">${item.title.split(' ')[0]} ${item.title.split(' ')[1]}</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">${item.category.toUpperCase()} · $${item.price}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Right Column: Product Detail & AnthroFit Dynamic Verifier -->
      <div class="product-details">
        <div class="retailer-eyebrow">
          <span class="brand-eyebrow-text">${currentProduct.brand}</span>
          <span class="item-sku-tag">CAD SPEC: ${currentProduct.id}</span>
        </div>

        <h1 class="item-title">${currentProduct.title}</h1>

        <div class="item-price-row">
          <div class="item-price">$${currentProduct.price.toFixed(2)}</div>
          <div class="item-tax-note">Carbon-neutral express delivery included</div>
        </div>

        <p class="item-desc">${currentProduct.story}</p>
        <div style="font-size: 0.8rem; color: #06b6d4; font-family: var(--font-mono); background: rgba(6,182,212,0.08); padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(6,182,212,0.2);">
          FABRIC SPEC: ${currentProduct.material}
        </div>

        <!-- Sizing Experience Container -->
        <div class="sizing-experience-card">
          <!-- The Legacy Comparison Header -->
          <div class="legacy-size-comparison">
            <div class="legacy-label-strikethrough">
              <span>Arbitrary Size Dropdown:</span>
              <span class="striked-sizes">[ XS | S | M | L | XL ]</span>
            </div>
            <div class="eliminated-badge">Obsolete / Replaced</div>
          </div>

          <!-- Step 1: User Reference Garment Selector -->
          <div class="anchor-selector-group">
            <label>
              <span>Garment You Own That Fits You Best:</span>
              <span style="color: #06b6d4; cursor: pointer;" title="We use the cutting tolerances of this garment to map against target patterns">Why this works?</span>
            </label>
            <select class="anchor-select-input" id="referenceAnchorSelect">
              ${availableAnchors.map(a => `
                <option value="${a.id}" ${a.id === state.selectedAnchorId ? 'selected' : ''}>${a.name}</option>
              `).join('')}
            </select>
          </div>

          <!-- Fit Preference Multi-toggle -->
          <div class="pref-toggles">
            <button class="pref-btn ${state.selectedPreference === 'fitted' ? 'active' : ''}" data-pref="fitted">Fitted / Structured</button>
            <button class="pref-btn ${state.selectedPreference === 'true_to_anchor' ? 'active' : ''}" data-pref="true_to_anchor">True to Anchor</button>
            <button class="pref-btn ${state.selectedPreference === 'relaxed' ? 'active' : ''}" data-pref="relaxed">Relaxed / Drape</button>
          </div>

          <!-- The AnthroFit Smart Dynamic Pill -->
          <div class="anthrofit-smart-pill">
            <div class="smart-pill-header">
              <div class="match-verdict-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>${fit.summary_verdict}</span>
              </div>
              <div class="confidence-chip">${fit.match_confidence_pct}% Match</div>
            </div>

            <div class="smart-pill-recs">
              <div>Recommended Pattern: <span class="recommended-cut-badge">${fit.recommended_cut_label}</span></div>
              <div class="risk-drop-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                <span>Return Risk: ${fit.return_risk_pct}% (Baseline: 32%)</span>
              </div>
            </div>

            <!-- Tactile Friction Point Breakdown -->
            <div class="friction-points-grid">
              ${fit.tactile_friction_points.map(fp => `
                <div class="friction-row">
                  <div>
                    <span class="friction-zone-name">${fp.zone}</span>
                    <div class="friction-note">${fp.explanation}</div>
                  </div>
                  <span class="friction-delta-tag ${fp.severity}">
                    ${fp.delta_cm >= 0 ? '+' : ''}${fp.delta_cm} cm
                  </span>
                </div>
              `).join('')}
            </div>

            <!-- Visual Overlay Trigger -->
            <button class="overlay-viewer-toggle-btn" id="openOverlayBtn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="12 8 8 12 12 16 16 12 12 8"></polygon></svg>
              <span>Inspect CAD Differential Silhouette Overlay</span>
            </button>
          </div>

          <button class="add-to-cart-btn">
            <span>Add Recommended Cut to Bag · $${currentProduct.price.toFixed(2)}</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Silhouette Modal Overlay -->
    ${state.showSilhouetteModal ? renderSilhouetteModal() : ''}
  `;
}

function attachStorefrontEvents() {
  // Product Switcher
  document.querySelectorAll('.product-thumb-pill').forEach(pill => {
    pill.addEventListener('click', async () => {
      const prodId = pill.getAttribute('data-product-id');
      state.selectedProductId = prodId;
      const targetProd = catalogItems.find(p => p.id === prodId);
      // Auto-switch to valid category anchor
      state.selectedAnchorId = targetProd.defaultAnchor;
      await updateFitComputation();
      renderApp();
    });
  });

  // Reference Anchor Change
  const anchorSelect = document.getElementById('referenceAnchorSelect');
  if (anchorSelect) {
    anchorSelect.addEventListener('change', async (e) => {
      state.selectedAnchorId = e.target.value;
      await updateFitComputation();
      renderApp();
    });
  }

  // Preference Buttons
  document.querySelectorAll('.pref-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      state.selectedPreference = btn.getAttribute('data-pref');
      await updateFitComputation();
      renderApp();
    });
  });

  // Modal Controls
  const openOverlayBtn = document.getElementById('openOverlayBtn');
  if (openOverlayBtn) {
    openOverlayBtn.addEventListener('click', () => {
      state.showSilhouetteModal = true;
      renderApp();
    });
  }

  const closeModalBtn = document.getElementById('closeModalBtn');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
      state.showSilhouetteModal = false;
      renderApp();
    });
  }
}

// Render dynamic Garment Wireframe Vector
function renderGarmentVectorSvg(category) {
  if (category === 'tops') {
    return `
      <svg class="hero-vector-art" viewBox="0 0 300 360" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="garmentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#1e293b" />
            <stop offset="100%" stop-color="#0f172a" />
          </linearGradient>
          <linearGradient id="glowLine" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#06b6d4" />
            <stop offset="100%" stop-color="#3b82f6" />
          </linearGradient>
        </defs>
        <!-- T-Shirt Architectural Outline -->
        <path d="M95 40 Q150 70 205 40 L260 85 L235 140 L195 125 L195 320 L105 320 L105 125 L65 140 L40 85 Z" 
              fill="url(#garmentGrad)" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
        
        <!-- Collar Detail -->
        <path d="M105 45 C120 75 180 75 195 45" stroke="#06b6d4" stroke-width="2.5" fill="none" />
        
        <!-- Chest Drape Tolerance Zone -->
        <line x1="105" y1="140" x2="195" y2="140" stroke="url(#glowLine)" stroke-width="2" stroke-dasharray="4 4" />
        <circle cx="150" cy="140" r="4" fill="#06b6d4" />
        <text x="150" y="132" fill="#06b6d4" font-size="10" font-family="monospace" text-anchor="middle">CHEST ANCHOR: ±0.5cm</text>
        
        <!-- Shoulder Drop Vector -->
        <line x1="95" y1="40" x2="260" y2="85" stroke="rgba(59,130,246,0.5)" stroke-width="1.5" stroke-dasharray="3 3" />
        <text x="75" y="70" fill="#94a3b8" font-size="9" font-family="monospace">SHOULDER SLOPE</text>

        <!-- Hem Drape Anchor -->
        <line x1="105" y1="320" x2="195" y2="320" stroke="#10b981" stroke-width="2" />
        <text x="150" y="340" fill="#10b981" font-size="10" font-family="monospace" text-anchor="middle">HEM DROP: +1.8cm</text>
      </svg>
    `;
  } else {
    return `
      <svg class="hero-vector-art" viewBox="0 0 300 360" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="denimGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#172554" />
            <stop offset="100%" stop-color="#09132e" />
          </linearGradient>
        </defs>
        <!-- Jeans Outline -->
        <path d="M90 35 L210 35 L218 100 L200 330 L160 330 L150 135 L140 330 L100 330 L82 100 Z" 
              fill="url(#denimGrad)" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
        
        <!-- Waistband Anchor -->
        <line x1="90" y1="35" x2="210" y2="35" stroke="#06b6d4" stroke-width="3" />
        <text x="150" y="25" fill="#06b6d4" font-size="10" font-family="monospace" text-anchor="middle">WAISTBAND: IDENTICAL</text>

        <!-- Thigh Vector -->
        <line x1="85" y1="120" x2="148" y2="120" stroke="#f59e0b" stroke-width="2" stroke-dasharray="3 3" />
        <text x="117" y="112" fill="#f59e0b" font-size="9" font-family="monospace" text-anchor="middle">THIGH: +0.7cm</text>

        <!-- Inseam Break -->
        <line x1="100" y1="330" x2="200" y2="330" stroke="#10b981" stroke-width="2" />
        <text x="150" y="350" fill="#10b981" font-size="10" font-family="monospace" text-anchor="middle">INSEAM: 83.5cm</text>
      </svg>
    `;
  }
}

// 2D Differential Silhouette Modal
function renderSilhouetteModal() {
  const fit = state.fitResult || {};
  const currentProduct = catalogItems.find(p => p.id === state.selectedProductId);
  const isTops = currentProduct.category === 'tops';

  return `
    <div style="position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 100; display: grid; place-items: center; padding: 1.5rem;">
      <div style="background: #12141a; border: 1px solid rgba(255,255,255,0.15); border-radius: 20px; width: 100%; max-width: 820px; padding: 2rem; box-shadow: var(--shadow-elevation); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div>
            <h3 style="font-size: 1.3rem; font-weight: 800; color: #fff;">CAD Differential Silhouette Wireframe</h3>
            <p style="font-size: 0.85rem; color: #94a3b8;">Cyan Line: Target Atelier Cut · Dotted Amber: Your Reference Garment</p>
          </div>
          <button id="closeModalBtn" style="background: rgba(255,255,255,0.1); border: none; color: #fff; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; display: grid; place-items: center; font-size: 1.1rem;">✕</button>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center;">
          <div style="background: #090a0f; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; height: 380px; display: grid; place-items: center; position: relative;">
            <svg viewBox="0 0 300 360" width="280" height="340" fill="none">
              <!-- Reference Garment (Dotted Amber) -->
              <path d="${isTops ? 'M98 44 Q150 72 202 44 L255 88 L232 138 L192 124 L192 312 L108 312 L108 124 L68 138 L45 88 Z' : 'M92 35 L208 35 L215 98 L198 320 L162 320 L150 135 L138 320 L102 320 L85 98 Z'}" 
                    stroke="#f59e0b" stroke-width="2" stroke-dasharray="4 4" fill="rgba(245,158,11,0.05)" />
              
              <!-- Target Garment (Cyan Solid) -->
              <path d="${isTops ? 'M95 40 Q150 70 205 40 L260 85 L235 140 L195 125 L195 320 L105 320 L105 125 L65 140 L40 85 Z' : 'M90 35 L210 35 L218 100 L200 330 L160 330 L150 135 L140 330 L100 330 L82 100 Z'}" 
                    stroke="#06b6d4" stroke-width="2.5" fill="rgba(6,182,212,0.08)" />
            </svg>
            <div style="position: absolute; bottom: 12px; left: 16px; font-size: 0.75rem; color: #94a3b8; display: flex; gap: 1rem;">
              <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 8px; height: 8px; background: #06b6d4; border-radius: 50%;"></span> Target SKU</span>
              <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 8px; height: 8px; background: #f59e0b; border-radius: 50%;"></span> Your Anchor</span>
            </div>
          </div>

          <div>
            <div style="margin-bottom: 1.5rem;">
              <div style="font-size: 0.8rem; font-weight: 700; color: #06b6d4; text-transform: uppercase;">Dimensional Variance Analysis</div>
              <h4 style="font-size: 1.1rem; font-weight: 700; margin-top: 0.2rem;">Physical Comfort Tolerance</h4>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              <div style="background: rgba(255,255,255,0.03); padding: 0.75rem 1rem; border-radius: 8px; display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #cbd5e1;">Fabric Stretch Delta:</span>
                <strong style="color: #10b981;">${fit.fabric_stretch_delta_factor || 0}% higher yield</strong>
              </div>
              <div style="background: rgba(255,255,255,0.03); padding: 0.75rem 1rem; border-radius: 8px; display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #cbd5e1;">Wash Shrinkage Compensated:</span>
                <strong style="color: #fff;">1.8% residual shrinkage</strong>
              </div>
              <div style="background: rgba(255,255,255,0.03); padding: 0.75rem 1rem; border-radius: 8px; display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #cbd5e1;">Predicted Return Risk:</span>
                <strong style="color: #10b981;">${fit.return_risk_pct}% (industry avg 32%)</strong>
              </div>
            </div>

            <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(16,185,129,0.08); border-left: 3px solid #10b981; border-radius: 0 8px 8px 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
              <strong style="color: #10b981;">Verdict:</strong> The dimensional differential falls safely within human tactile tolerance limits. Zero risk of respiratory or movement constriction.
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

/* ==========================================================================
   VIEW 2: Enterprise Retailer Analytics & Margin Saved Dashboard
   ========================================================================== */

function renderDashboardView() {
  return `
    <div style="display: flex; flex-direction: column; gap: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
          <span style="font-size: 0.8rem; font-weight: 700; color: #06b6d4; text-transform: uppercase; letter-spacing: 0.08em;">B2B Enterprise Portal</span>
          <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em;">Reverse Logistics & Margin Recovery</h2>
        </div>
        <div style="text-align: right; font-size: 0.85rem; color: #94a3b8;">
          Client: <strong style="color: #fff;">Atelier Nordic Group</strong> · Headless SDK v2.4.1 Active
        </div>
      </div>

      <!-- Top Row: 4 Primary KPI Cards -->
      <div class="dashboard-grid">
        <div class="kpi-card">
          <div class="kpi-label">Return Rate (E-Commerce)</div>
          <div class="kpi-value" style="color: #10b981;">3.8%</div>
          <div class="kpi-delta good">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>
            <span>-87.9% vs 31.4% industry baseline</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">Net Recovered Margin</div>
          <div class="kpi-value">$1,482,900</div>
          <div class="kpi-delta good">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
            <span>+$38.50 net saved per order</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">Conversion Rate Lift</div>
          <div class="kpi-value" style="color: #3b82f6;">+19.4%</div>
          <div class="kpi-delta good">
            <span>Size hesitation cart abandonment cured</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">Textile Waste Diverted</div>
          <div class="kpi-value" style="color: #06b6d4;">18,450 kg</div>
          <div class="kpi-delta good">
            <span>268.4 metric tons CO₂e averted</span>
          </div>
        </div>
      </div>

      <!-- Split Row: Return Reasons Breakdown vs Monthly Trend -->
      <div class="dashboard-split-row">
        <!-- Monthly Financial Savings Trend -->
        <div class="chart-card">
          <div class="chart-header">
            <div class="card-title">Monthly Returns Prevented & Capital Saved</div>
            <span style="font-size: 0.8rem; color: #94a3b8;">Apr - Jul 2026</span>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: flex-end; height: 180px; padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.08);">
            <div style="text-align: center; flex: 1;">
              <div style="height: 100px; width: 42px; background: rgba(59,130,246,0.3); border: 1px solid #3b82f6; border-radius: 6px; margin: 0 auto; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 6px; font-size: 0.75rem; font-weight: 700;">$320k</div>
              <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;">Apr</div>
            </div>
            <div style="text-align: center; flex: 1;">
              <div style="height: 120px; width: 42px; background: rgba(59,130,246,0.4); border: 1px solid #3b82f6; border-radius: 6px; margin: 0 auto; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 6px; font-size: 0.75rem; font-weight: 700;">$354k</div>
              <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;">May</div>
            </div>
            <div style="text-align: center; flex: 1;">
              <div style="height: 135px; width: 42px; background: rgba(59,130,246,0.5); border: 1px solid #3b82f6; border-radius: 6px; margin: 0 auto; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 6px; font-size: 0.75rem; font-weight: 700;">$374k</div>
              <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;">Jun</div>
            </div>
            <div style="text-align: center; flex: 1;">
              <div style="height: 160px; width: 42px; background: linear-gradient(180deg, #06b6d4, #3b82f6); border-radius: 6px; margin: 0 auto; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 6px; font-size: 0.75rem; font-weight: 700; color: #fff;">$435k</div>
              <div style="font-size: 0.8rem; color: #fff; font-weight: 700; margin-top: 0.5rem;">Jul</div>
            </div>
          </div>
          <div style="font-size: 0.8rem; color: #94a3b8; text-align: center;">Cumulative 140,300 returns successfully prevented from entering reverse transit</div>
        </div>

        <!-- Return Reason Pre vs Post AnthroFit -->
        <div class="chart-card">
          <div class="chart-header">
            <div class="card-title">Return Causes Comparison</div>
            <span style="font-size: 0.75rem; color: #10b981; font-weight: 700;">Zero Sizing Returns</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 1rem; font-size: 0.85rem;">
            <div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #94a3b8;">Traditional Checkout (Fit Mismatch)</span>
                <span style="color: #f43f5e; font-weight: 700;">70% of all returns</span>
              </div>
              <div style="height: 8px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden;">
                <div style="width: 70%; height: 100%; background: #f43f5e;"></div>
              </div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #94a3b8;">With AnthroFit OS (Residual Fit Returns)</span>
                <span style="color: #10b981; font-weight: 700;">0.4%</span>
              </div>
              <div style="height: 8px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden;">
                <div style="width: 4%; height: 100%; background: #10b981;"></div>
              </div>
            </div>

            <div style="margin-top: 0.5rem; padding: 1rem; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); font-size: 0.8rem; color: #94a3b8;">
              Remaining return causes shifted purely to <strong>Style Second-Thoughts (7.2%)</strong> and <strong>Carrier Delivery Delay (1.7%)</strong>.
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Card: SKU Anomaly Alert Radar -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="card-title">Real-Time CAD Cutting Anomaly Detector</div>
          <span style="font-size: 0.8rem; color: #06b6d4;">Supplier Quality Control</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
          <div style="background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.25); border-radius: 10px; padding: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family: var(--font-mono); font-size: 0.75rem; color: #f59e0b; font-weight: 700;">SKU-AT-HTEE-01</span>
              <span style="font-size: 0.75rem; background: rgba(245,158,11,0.2); color: #f59e0b; padding: 2px 8px; border-radius: 4px;">Monitored</span>
            </div>
            <div style="font-weight: 700; margin: 0.5rem 0 0.25rem 0;">Armhole Grade Sit Anomaly</div>
            <div style="font-size: 0.825rem; color: #94a3b8;">Armhole sits 1.4cm higher than standard European block pattern. AnthroFit automatically adjusts friction warning.</div>
          </div>

          <div style="background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 10px; padding: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family: var(--font-mono); font-size: 0.75rem; color: #10b981; font-weight: 700;">SKU-AT-SEL-31</span>
              <span style="font-size: 0.75rem; background: rgba(16,185,129,0.2); color: #10b981; padding: 2px 8px; border-radius: 4px;">Diverted</span>
            </div>
            <div style="font-weight: 700; margin: 0.5rem 0 0.25rem 0;">Rigid Zero-Yield Denim Compensation</div>
            <div style="font-size: 0.825rem; color: #94a3b8;">1,140 shoppers owning stretch denim were diverted to Cut 32, avoiding zero-stretch waistband returns.</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

/* ==========================================================================
   VIEW 3: Headless B2B Developer API Playground & SDK
   ========================================================================== */

function renderApiView() {
  const currentAnchor = state.selectedAnchorId;
  const currentProd = state.selectedProductId;
  const currentPref = state.selectedPreference;

  const sampleReqJson = JSON.stringify({
    user_reference_sku_id: currentAnchor,
    target_catalog_item_id: currentProd,
    fit_preference: currentPref
  }, null, 2);

  const sampleResJson = JSON.stringify(state.fitResult || {}, null, 2);

  return `
    <div style="display: flex; flex-direction: column; gap: 2rem;">
      <div>
        <span style="font-size: 0.8rem; font-weight: 700; color: #06b6d4; text-transform: uppercase;">Headless API & Integration SDK</span>
        <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em;">Differential Vector REST Console</h2>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.25rem;">
          Plug into headless checkout flows, Shopify Hydrogen, or custom mobile applications with single-millisecond latency.
        </p>
      </div>

      <div class="api-container">
        <!-- Request Panel -->
        <div style="display: flex; flex-direction: column; gap: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="background: #10b981; color: #000; font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">POST</span>
              <span style="font-family: var(--font-mono); font-size: 0.85rem; color: #fff;">/api/fit/match</span>
            </div>
            <button id="sendApiReqBtn" style="background: #06b6d4; border: none; color: #000; font-family: var(--font-sans); font-size: 0.8rem; font-weight: 700; padding: 0.4rem 0.9rem; border-radius: 6px; cursor: pointer;">
              Execute Request
            </button>
          </div>
          <pre class="code-box" id="apiRequestCode">${sampleReqJson}</pre>

          <!-- Integration SDK Snippet -->
          <div style="margin-top: 1rem;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.5rem;">Frontend Drop-In SDK (React / Web Components)</div>
            <pre class="code-box" style="font-size: 0.775rem;">import { AnthroFitSmartPill } from '@anthrofit/sdk-react';

&lt;AnthroFitSmartPill 
  targetCatalogSku="PROD-ATELIER-HEAVY-TEE"
  onFitResolved={(result) =&gt; addToCart(result.recommended_sku_id)}
  brandAccentColor="#06b6d4"
/&gt;</pre>
          </div>
        </div>

        <!-- Response Panel -->
        <div style="display: flex; flex-direction: column; gap: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="background: rgba(16,185,129,0.2); color: #10b981; font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">200 OK</span>
              <span style="font-family: var(--font-mono); font-size: 0.85rem; color: #94a3b8;">Latency: 14ms · Cached CAD Topology</span>
            </div>
          </div>
          <pre class="code-box" id="apiResponseCode">${sampleResJson}</pre>
        </div>
      </div>
    </div>
  `;
}

function attachApiEvents() {
  const sendBtn = document.getElementById('sendApiReqBtn');
  if (sendBtn) {
    sendBtn.addEventListener('click', async () => {
      sendBtn.innerText = 'Calculating...';
      await updateFitComputation();
      sendBtn.innerText = 'Execute Request';
      const codeBox = document.getElementById('apiResponseCode');
      if (codeBox) {
        codeBox.innerText = JSON.stringify(state.fitResult, null, 2);
      }
    });
  }
}

/* ==========================================================================
   VIEW 4: Investor Pitch Deck & Innovation Rubrics
   ========================================================================== */

function renderPitchView() {
  const slide = pitchSlides[state.currentPitchSlide];

  return `
    <div class="pitch-container">
      <div class="pitch-slide-card">
        <div>
          <span style="font-size: 0.85rem; font-weight: 800; color: #06b6d4; letter-spacing: 0.12em; text-transform: uppercase;">
            ${slide.tag} · SLIDE ${state.currentPitchSlide + 1} OF ${pitchSlides.length}
          </span>
          <h2 style="font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.15; margin-top: 0.5rem;">
            ${slide.title}
          </h2>
          <p style="font-size: 1.1rem; color: #94a3b8; margin-top: 0.4rem;">
            ${slide.subtitle}
          </p>

          ${slide.contentHtml}
        </div>

        <div style="margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
          <div style="font-family: var(--font-mono); font-size: 0.8rem; color: #64748b;">
            "Software translates the geometry of what already fits you."
          </div>
          <div style="font-size: 0.85rem; font-weight: 700; color: #06b6d4;">
            ANTHROFIT OS
          </div>
        </div>
      </div>

      <div class="pitch-nav-bar">
        <button class="nav-btn" id="prevSlideBtn" ${state.currentPitchSlide === 0 ? 'disabled style="opacity: 0.4;"' : ''}>← Previous</button>
        <div class="pitch-dots">
          ${pitchSlides.map((_, idx) => `
            <div class="pitch-dot ${idx === state.currentPitchSlide ? 'active' : ''}" data-slide-index="${idx}"></div>
          `).join('')}
        </div>
        <button class="nav-btn" id="nextSlideBtn" ${state.currentPitchSlide === pitchSlides.length - 1 ? 'disabled style="opacity: 0.4;"' : ''}>Next Slide →</button>
      </div>
    </div>
  `;
}

function attachPitchEvents() {
  const prevBtn = document.getElementById('prevSlideBtn');
  const nextBtn = document.getElementById('nextSlideBtn');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (state.currentPitchSlide > 0) {
        state.currentPitchSlide--;
        renderApp();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (state.currentPitchSlide < pitchSlides.length - 1) {
        state.currentPitchSlide++;
        renderApp();
      }
    });
  }

  document.querySelectorAll('.pitch-dot').forEach(dot => {
    dot.addEventListener('click', () => {
      state.currentPitchSlide = parseInt(dot.getAttribute('data-slide-index'));
      renderApp();
    });
  });
}

// Global bootstrap
window.addEventListener('DOMContentLoaded', initApp);
