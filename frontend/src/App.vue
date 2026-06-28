<template>
  <div id="app">
    <nav class="app-nav">
      <div class="nav-brand">
        <span class="logo">⌨️</span>
        <h2>Claude Panel</h2>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <rect x="2" y="4" width="20" height="16" rx="2"/>
            <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M7 16h10"/>
          </svg>
          控制面板
        </router-link>
        <router-link to="/ssh" class="nav-link ssh-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <polyline points="4 17 10 11 4 5"/>
            <line x1="12" y1="19" x2="20" y2="19"/>
          </svg>
          SSH 终端
        </router-link>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.app-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  font-size: 2rem;
}

.nav-brand h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ssh-link {
  background: rgba(16, 185, 129, 0.3);
  border: 1px solid rgba(16, 185, 129, 0.5);
}

.ssh-link:hover {
  background: rgba(16, 185, 129, 0.4);
}

.ssh-link.router-link-active {
  background: rgba(16, 185, 129, 0.5);
}
</style>
