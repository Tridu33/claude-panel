// 鉴权辅助:封装 token 存储、登录/登出/校验、WebSocket URL
const TOKEN_KEY = 'panel_token'

// 鉴权状态缓存:null=未知, true=已登录, false=未登录
let _authed = null

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function isAuthed() {
  return _authed === true
}

// 校验当前会话是否有效(走 cookie)
export async function checkAuth() {
  try {
    const r = await fetch('/api/auth/me', { credentials: 'same-origin' })
    if (r.ok) {
      const j = await r.json()
      _authed = !!j.ok
      return _authed
    }
  } catch (e) {
    // 网络错误,保持未知状态
  }
  _authed = false
  return false
}

// 从响应中安全提取 JSON，处理后端不可用等异常
async function tryParseJson(resp) {
  const ct = resp.headers.get('content-type') || ''
  if (!ct.includes('application/json')) {
    const text = await resp.text().catch(() => '')
    throw new Error(text ? '后端服务异常(非JSON响应)' : '后端未响应')
  }
  return resp.json()
}

export async function login(account, password) {
  const r = await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ account, password }),
  })
  const j = await tryParseJson(r)
  if (j.ok) {
    setToken(j.token || '')
    _authed = true
  }
  return j
}

export async function logout() {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'same-origin',
    })
  } catch (e) {
    // 忽略网络错误,前端仍清除本地态
  }
  setToken('')
  _authed = false
}

// 构造带 token 的 WebSocket URL(同源 cookie 也会自动带上,token 作为双保险)
export function wsUrl(path) {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const t = getToken()
  return `${proto}//${window.location.host}${path}${t ? '?token=' + encodeURIComponent(t) : ''}`
}
