<template>
  <div id="app">
    <nav v-if="$route.name !== 'Login'" class="app-nav">
      <div class="nav-brand">
        <span class="logo">⌨️</span>
        <h2>Claude Panel</h2>
      </div>
      <div id="nav-controls" class="nav-controls"></div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <rect x="2" y="4" width="20" height="16" rx="2"/>
            <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M7 16h10"/>
          </svg>
          控制面板
        </router-link>
        <a class="nav-link logout-link" href="#" @click.prevent="onLogout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          登出
        </a>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
import { logout } from './auth'

export default {
  name: 'App',
  methods: {
    async onLogout() {
      await logout()
      this.$router.replace({ name: 'Login' })
    },
  },
}
</script>

<style scoped>
.app-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem clamp(0.75rem, 2vw, 2rem);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: clamp(0.25rem, 0.75vw, 0.75rem);
  flex-shrink: 0;
}

.logo {
  font-size: clamp(1.25rem, 2.5vw, 2rem);
}

.nav-brand h2 {
  margin: 0;
  font-size: clamp(0.9rem, 1.5vw, 1.25rem);
  font-weight: 600;
  white-space: nowrap;
}

.nav-controls {
  display: flex;
  align-items: center;
  flex: 1 1 auto;
  justify-content: center;
  min-width: 0;
}

.nav-links {
  display: flex;
  gap: clamp(0.25rem, 0.75vw, 1rem);
  flex-shrink: 0;
  flex-wrap: wrap;
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

.logout-link {
  background: rgba(239, 68, 68, 0.25);
  border: 1px solid rgba(239, 68, 68, 0.5);
}

.logout-link:hover {
  background: rgba(239, 68, 68, 0.45);
  color: white;
}

@media (max-width: 768px) {
  .app-nav {
    padding: 0.5rem 0.75rem;
    gap: 0.4rem;
  }

  .nav-brand h2 {
    font-size: 0.85rem;
  }

  .nav-link {
    padding: 0.35rem 0.6rem;
    font-size: 0.8rem;
    gap: 0.3rem;
  }

  .nav-link svg {
    width: 14px;
    height: 14px;
  }

  .nav-controls {
    order: 3;
    flex: 1 1 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .nav-brand h2 {
    display: none;
  }

  .nav-links {
    gap: 0.25rem;
  }

  .nav-link {
    padding: 0.3rem 0.5rem;
    font-size: 0.75rem;
  }
}
</style>
