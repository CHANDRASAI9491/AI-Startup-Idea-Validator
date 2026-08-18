import streamlit as st


def render_top_navbar() -> None:
    """Renders the dark top navigation bar matching the design reference."""
    st.markdown("""
<div class="saas-top-navbar">
  <div class="top-nav-left">
    <div class="top-nav-brand">
      <span class="brand-logo-dot"></span>
      <span class="brand-name">Startup Validator</span>
    </div>
  </div>
  <div class="top-nav-right">
    <span class="top-nav-link">Reports</span>
    <span class="top-nav-link">Settings</span>
    <span class="top-nav-link">About</span>
    <div class="top-nav-user">
      <span class="user-avatar">U</span>
      <span class="user-name">Workspace</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_header() -> None:
    """Renders the main header hero section with clean typography and subtle analytical illustration."""
    render_top_navbar()

    st.markdown("""
<div class="saas-hero-container">
  <div class="hero-content">
    <h1 class="saas-hero-heading">
      Development of AI Based Startup Idea Validator<br/>
      <span class="hero-subtext">with Market Analysis Assistance</span>
    </h1>
    <p class="saas-hero-subheading">
      Turn your idea into an evidence-based startup validation report.
    </p>
  </div>
  <div class="hero-illustration-container">
    <svg class="hero-illustration-svg" viewBox="0 0 240 140" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Background subtle grid/chart container -->
      <rect x="10" y="10" width="220" height="120" rx="12" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="1.5"/>
      <line x1="30" y1="105" x2="210" y2="105" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="3 3"/>
      <line x1="30" y1="75" x2="210" y2="75" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="3 3"/>
      <line x1="30" y1="45" x2="210" y2="45" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="3 3"/>
      
      <!-- Growth Area Gradient -->
      <path d="M30 95 Q 75 90, 110 65 T 180 35 L 210 25 L 210 105 L 30 105 Z" fill="url(#hero_area_grad)" opacity="0.6"/>
      <!-- Growth Trend Line -->
      <path d="M30 95 Q 75 90, 110 65 T 180 35 L 210 25" stroke="#2563EB" stroke-width="3" stroke-linecap="round"/>
      
      <!-- Analytical Nodes -->
      <circle cx="30" cy="95" r="4" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
      <circle cx="95" cy="76" r="4" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
      <circle cx="145" cy="50" r="4" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
      <circle cx="210" cy="25" r="5" fill="#2563EB" stroke="#FFFFFF" stroke-width="2"/>
      
      <!-- Subtle Rocket / Launch Silhouette at Peak -->
      <g transform="translate(195, 8) scale(0.65)">
        <path d="M15 0C15 0 21 6 21 16C21 21 18 25 18 25L12 25C12 25 9 21 9 16C9 6 15 0 15 0Z" fill="#2563EB"/>
        <path d="M9 16L4 20L6 24L11 22" fill="#1D4ED8"/>
        <path d="M21 16L26 20L24 24L19 22" fill="#1D4ED8"/>
        <circle cx="15" cy="11" r="3" fill="#FFFFFF"/>
        <path d="M12 26C13.5 29 16.5 29 18 26C16.5 32 13.5 32 12 26Z" fill="#F59E0B"/>
      </g>
      
      <!-- Metric Mini Badge -->
      <rect x="25" y="22" width="68" height="24" rx="6" fill="#FFFFFF" stroke="#DBEAFE" stroke-width="1.2"/>
      <text x="32" y="38" font-family="Inter, sans-serif" font-size="10" font-weight="700" fill="#2563EB">Viability 84+</text>

      <defs>
        <linearGradient id="hero_area_grad" x1="120" y1="25" x2="120" y2="105" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.0"/>
        </linearGradient>
      </defs>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)
