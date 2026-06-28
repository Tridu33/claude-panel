/* app.js — Claude 键盘控制面板前端逻辑 */

const WS_URL = `ws://${location.host}/ws`;

let ws = null;
let reconnectTimer = null;

// ── DOM refs ────────────────────────────────────────────────
const wsBadge       = document.getElementById("ws-badge");
const lcdText       = document.getElementById("lcd-text");
const logList       = document.getElementById("log-list");
const modeSelect    = document.getElementById("mode-select");
const autoToggle    = document.getElementById("auto-approve-toggle");
const toggleState   = document.getElementById("toggle-state");
const lcdInput      = document.getElementById("lcd-input");
const sendLcdBtn    = document.getElementById("send-lcd");
const clearLogBtn   = document.getElementById("clear-log");

// ── WebSocket ──────────────────────────────────────────────
function connect() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    setBadge(true);
    clearTimeout(reconnectTimer);
  };

  ws.onclose = () => {
    setBadge(false);
    reconnectTimer = setTimeout(connect, 3000);
  };

  ws.onerror = () => ws.close();

  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.type === "state") applyState(data);
      if (data.type === "pong")  {}
    } catch {}
  };
}

function send(obj) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(obj));
  } else {
    // fallback: REST
    console.warn("WS not open, event dropped:", obj);
  }
}

// ── 状态渲染 ────────────────────────────────────────────────
function applyState(state) {
  // LCD
  if (state.lcd_message !== undefined) {
    lcdText.textContent = state.lcd_message;
    lcdText.classList.add("blink");
    setTimeout(() => lcdText.classList.remove("blink"), 500);
  }

  // LED
  if (state.led_status) {
    state.led_status.forEach((v, i) => {
      const el = document.getElementById(`led-${i}`);
      if (!el) return;
      el.classList.remove("on", "run");
      if (v === 1) el.classList.add("on");
      if (v === 2) el.classList.add("run");
    });
  }

  // Auto-approve toggle
  if (state.auto_approve !== undefined) {
    autoToggle.checked = state.auto_approve;
    toggleState.textContent = state.auto_approve ? "ON" : "OFF";
    toggleState.classList.toggle("active", state.auto_approve);
  }

  // Mode select
  if (state.current_mode !== undefined) {
    modeSelect.value = String(state.current_mode);
  }

  // Logs
  if (state.logs && Array.isArray(state.logs)) {
    renderLogs(state.logs);
  }
}

function renderLogs(logs) {
  // Prepend only the newest entry if it's new
  const latest = logs[logs.length - 1];
  if (!latest) return;

  // Check if already rendered
  const first = logList.firstChild;
  if (first && first.dataset.key === `${latest.time}-${latest.action}`) return;

  const li = document.createElement("li");
  li.dataset.key = `${latest.time}-${latest.action}`;
  li.innerHTML = `
    <span class="log-time">${latest.time}</span>
    <span class="log-action">${latest.action}</span>
    <span class="log-detail">${latest.detail || ""}</span>
  `;
  logList.prepend(li);

  // Keep max 30 entries
  while (logList.children.length > 30) {
    logList.removeChild(logList.lastChild);
  }
}

// ── 按键交互 ────────────────────────────────────────────────
document.querySelectorAll(".key-btn").forEach(btn => {
  btn.addEventListener("pointerdown", () => btn.classList.add("pressed"));
  btn.addEventListener("pointerup",   () => btn.classList.remove("pressed"));
  btn.addEventListener("pointerleave",() => btn.classList.remove("pressed"));

  btn.addEventListener("click", () => {
    const key = btn.dataset.key;
    triggerRipple(btn);
    send({ type: "keypress", key });

    // Optimistic LCD update
    const labels = { mic: "🎙 Listening…", yes: "✅ YES", no: "❌ NO", enter: "↵ Submit" };
    lcdText.textContent = labels[key] || key;
  });
});

function triggerRipple(btn) {
  const ripple = btn.querySelector(".key-ripple");
  if (!ripple) return;
  ripple.classList.remove("animate");
  void ripple.offsetWidth; // reflow
  ripple.style.width  = ripple.style.height = btn.offsetWidth * 1.6 + "px";
  ripple.style.left   = (btn.offsetWidth  / 2 - btn.offsetWidth * .8) + "px";
  ripple.style.top    = (btn.offsetHeight / 2 - btn.offsetWidth * .8) + "px";
  ripple.classList.add("animate");
}

// ── 拨杆 ────────────────────────────────────────────────────
autoToggle.addEventListener("change", () => {
  send({ type: "toggle_auto_approve" });
});

// ── 模式切换 ────────────────────────────────────────────────
modeSelect.addEventListener("change", () => {
  send({ type: "set_mode", mode: parseInt(modeSelect.value, 10) });
});

// ── LCD 自定义文字 ───────────────────────────────────────────
sendLcdBtn.addEventListener("click", () => {
  const msg = lcdInput.value.trim();
  if (!msg) return;
  fetch("/api/lcd", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg }),
  });
  lcdInput.value = "";
});
lcdInput.addEventListener("keydown", e => {
  if (e.key === "Enter") sendLcdBtn.click();
});

// ── 清空日志 ─────────────────────────────────────────────────
clearLogBtn.addEventListener("click", () => {
  logList.innerHTML = "";
});

// ── WS 状态指示 ──────────────────────────────────────────────
function setBadge(online) {
  wsBadge.textContent = online ? "WS 已连接" : "WS 断开";
  wsBadge.className   = online ? "badge badge-on" : "badge badge-off";
}

// ── LCD 闪烁动画 CSS（注入）────────────────────────────────
const style = document.createElement("style");
style.textContent = `
  @keyframes lcd-blink {
    0%,100% { opacity:1; }
    50%      { opacity:.4; }
  }
  #lcd-text.blink { animation: lcd-blink .4s ease; }
`;
document.head.appendChild(style);

// ── 启动 ────────────────────────────────────────────────────
connect();

// Ping keepalive every 25s
setInterval(() => send({ type: "ping" }), 25000);
