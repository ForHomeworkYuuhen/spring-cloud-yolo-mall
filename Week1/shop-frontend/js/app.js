// 网关地址（Spring Cloud Gateway）。商品目录为公开接口，无需令牌；
// 登录后服务端签发的 JWT 存 localStorage，下单等敏感操作才需带 Authorization: Bearer。
const GATEWAY = "http://localhost:9000";

// 推荐服务地址（个性化推荐 / ItemCF 协同过滤，基于天池用户行为数据）。默认本机 8124。
const REC_API = "http://localhost:8124";

// 与 t_product 一致的兜底数据（网关未启动时用）——即 YOLO 识别的 19 种零食；图标用 emoji 占位
const MOCK = [
  { id: 1,  name: "Ashi Mashi snacks",               price: 6.5,  emoji: "🍿", sales: 3200,  shop: "Ashi Mashi 旗舰店" },
  { id: 2,  name: "Chee pellet ketchup",             price: 5.0,  emoji: "🍿", sales: 4100,  shop: "Chee 旗舰店" },
  { id: 3,  name: "Chee pellet vinegar",             price: 5.0,  emoji: "🍿", sales: 3900,  shop: "Chee 旗舰店" },
  { id: 4,  name: "Cheetoz chili chips",             price: 8.5,  emoji: "🥔", sales: 15200, shop: "Cheetoz 旗舰店" },
  { id: 5,  name: "Cheetoz ketchup chips",           price: 8.5,  emoji: "🥔", sales: 18800, shop: "Cheetoz 旗舰店" },
  { id: 6,  name: "Cheetoz onion and parsley chips", price: 8.5,  emoji: "🥔", sales: 9400,  shop: "Cheetoz 旗舰店" },
  { id: 7,  name: "Cheetoz salty chips",             price: 8.0,  emoji: "🥔", sales: 21000, shop: "Cheetoz 旗舰店" },
  { id: 8,  name: "Cheetoz snack 30g",               price: 3.5,  emoji: "🍿", sales: 26500, shop: "Cheetoz 旗舰店" },
  { id: 9,  name: "Cheetoz snack 90g",               price: 7.9,  emoji: "🍿", sales: 17300, shop: "Cheetoz 旗舰店" },
  { id: 10, name: "Cheetoz vinegar chips",           price: 8.5,  emoji: "🥔", sales: 12600, shop: "Cheetoz 旗舰店" },
  { id: 11, name: "Cheetoz wheelsnack",              price: 6.0,  emoji: "🍿", sales: 8800,  shop: "Cheetoz 旗舰店" },
  { id: 12, name: "Maz Maz ketchup chips",           price: 7.5,  emoji: "🥔", sales: 11200, shop: "Maz Maz 旗舰店" },
  { id: 13, name: "Maz Maz potato sticks",           price: 6.5,  emoji: "🍟", sales: 10100, shop: "Maz Maz 旗舰店" },
  { id: 14, name: "Maz Maz salty chips",             price: 7.0,  emoji: "🥔", sales: 13400, shop: "Maz Maz 旗舰店" },
  { id: 15, name: "Maz Maz vinegar chips",           price: 7.5,  emoji: "🥔", sales: 9900,  shop: "Maz Maz 旗舰店" },
  { id: 16, name: "Mini Lina",                       price: 9.9,  emoji: "🍪", sales: 5600,  shop: "Mini Lina 旗舰店" },
  { id: 17, name: "Minoo cream biscuit",             price: 10.5, emoji: "🍪", sales: 7700,  shop: "Minoo 旗舰店" },
  { id: 18, name: "Naderi mini cookie",              price: 11.0, emoji: "🍪", sales: 6300,  shop: "Naderi 旗舰店" },
  { id: 19, name: "Naderi mini wafer",               price: 9.5,  emoji: "🍪", sales: 8200,  shop: "Naderi 旗舰店" },
];

// 拉商品：先试网关（真实微服务），失败回退 mock
async function fetchProducts() {
  const list = [];
  try {
    for (let id = 1; id <= 4; id++) {
      const r = await fetch(`${GATEWAY}/admin/products/${id}`, { signal: AbortSignal.timeout(1500) });
      if (!r.ok) throw 0;
      const p = await r.json();
      const m = MOCK.find(x => x.id === p.id) || {};
      // 用网关返回证明微服务在线 + 取真实价格；展示用干净的零食名（网关名带 —端口 负载均衡标记）
      list.push({ id: p.id, name: m.name || p.name, price: p.price, emoji: m.emoji || "📦", sales: m.sales || 0, shop: m.shop || "官方旗舰店" });
    }
    // 真实只有4条，补充 mock 让首页更丰满
    return list.concat(MOCK.slice(4));
  } catch (e) {
    return MOCK; // 网关未启动 → 用兜底数据
  }
}

// 个性化推荐：调推荐服务拿到推荐的商品ID，再从商品目录取出对应商品；失败按销量兜底。
// 推荐结果由 recommend/ 下的 ItemCF 协同过滤模型（基于天池用户行为数据）产出，自动展示无需按钮。
async function fetchRecommend(user, allProducts, n = 4) {
  try {
    const url = `${REC_API}/recommend?user_id=${encodeURIComponent(user || "guest")}&n=${n}`;
    const r = await fetch(url, { signal: AbortSignal.timeout(2000) });
    if (!r.ok) throw 0;
    const data = await r.json();
    const ids = data.item_ids || [];
    const byId = Object.fromEntries(allProducts.map(p => [p.id, p]));
    const recs = ids.map(id => byId[id]).filter(Boolean);
    if (recs.length) return recs;
    throw 0;
  } catch (e) {
    return [...allProducts].sort((a, b) => b.sales - a.sales).slice(0, n); // 推荐服务未起 → 按销量
  }
}

const PH = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="1"/><circle cx="8.5" cy="10" r="1.5"/><path d="M3 16l5-4 4 3 3-2 6 5"/></svg>';
function cardHTML(p) {
  return `<div class="card">
    <a class="card-link" href="product.html?id=${p.id}">
      <div class="ph">${p.emoji ? '<span class="emoji">' + p.emoji + '</span>' : PH}</div>
      <div class="cname">${p.name}</div>
      <div class="cprice"><small>¥</small>${Number(p.price).toFixed(2)}</div>
      <div class="cmeta">${p.sales ? p.sales + '+ 已售 · ' : ''}${p.shop || ''}</div>
    </a>
    <button class="add-btn" onclick="addToCart(${p.id})">加入购物车</button>
  </div>`;
}

// 登录态（演示用 localStorage；真实应走用户服务+JWT，密码不在前端明文处理）
function currentUser() { return localStorage.getItem("user"); }
function renderUser() {
  const u = currentUser();
  const el = document.getElementById("userArea");
  if (!el) return;
  el.innerHTML = u
    ? `<span class="hi">Hi，${u}</span> <a href="#" onclick="logout()">退出</a>`
    : `请 <a class="hi" href="login.html">登录</a> <a href="login.html">注册</a>`;
}
function logout() { localStorage.removeItem("user"); localStorage.removeItem("token"); renderUser(); updateCartBadge(); }

// ---- 令牌 / 账户入口 ----
function token() { return localStorage.getItem("token") || ""; }
function goAccount() { location.href = currentUser() ? "profile.html" : "login.html"; }

// ---- 购物车（localStorage 存 {id,qty}，展示时按商品目录映射） ----
function getCart() { try { return JSON.parse(localStorage.getItem("cart") || "[]"); } catch (e) { return []; } }
function saveCart(c) { localStorage.setItem("cart", JSON.stringify(c)); updateCartBadge(); }
function cartCount() { return getCart().reduce((n, it) => n + (it.qty || 1), 0); }
function addToCart(id, qty) {
  qty = qty || 1;
  const c = getCart();
  const it = c.find(x => x.id === id);
  if (it) it.qty += qty; else c.push({ id, qty });
  saveCart(c);
  toast("已加入购物车", "ok");
}
function updateCartBadge() {
  const b = document.getElementById("cartBadge");
  if (!b) return;
  const n = cartCount();
  b.textContent = n > 0 ? String(n) : "";
  b.style.display = n > 0 ? "" : "none";
}

// 统一的 Toast 提示（替代浏览器原生 alert）
function toast(msg, type) {
  const t = document.createElement("div");
  t.className = "toast" + (type === "error" ? " err" : "") + (type === "ok" ? " ok" : "");
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add("show"));
  setTimeout(() => { t.classList.remove("show"); setTimeout(() => t.remove(), 280); }, 2200);
}

// ---- AI 客服：知识图谱(neo4j) + LLM 问答，悬浮聊天窗（所有页面都挂） ----
const QA_API = "http://localhost:8125";
function initChat() {
  if (document.querySelector(".chat-fab")) return;
  const fab = document.createElement("div");
  fab.className = "chat-fab";
  fab.title = "AI 客服";
  fab.innerHTML = '<svg viewBox="0 0 24 24"><path d="M21 11.5a8.4 8.4 0 0 1-12 7.6L3 21l1.9-6A8.4 8.4 0 1 1 21 11.5z"/></svg>';
  const panel = document.createElement("div");
  panel.className = "chat-panel";
  panel.innerHTML =
    '<div class="chat-head"><span>AI 客服 <small>知识图谱 + LLM</small></span><span class="chat-close">×</span></div>' +
    '<div class="chat-body" id="chatBody"></div>' +
    '<div class="chat-quick" id="chatQuick"></div>' +
    '<div class="chat-input"><input id="chatIn" placeholder="问问零食，如“有哪些薯片”…"><button id="chatSend">发送</button></div>';
  document.body.append(fab, panel);

  const body = panel.querySelector("#chatBody");
  const inp = panel.querySelector("#chatIn");
  const quick = panel.querySelector("#chatQuick");
  let booted = false;

  function add(text, who) {
    const d = document.createElement("div");
    d.className = "msg " + who;
    d.textContent = text;
    body.appendChild(d);
    body.scrollTop = body.scrollHeight;
    return d;
  }
  function boot() {
    if (booted) return; booted = true;
    add("你好，我是粤海购 AI 客服～可以问我零食、品牌、价格相关的问题。", "bot");
    ["有哪些薯片？", "Cheetoz 有什么", "最便宜的零食"].forEach(q => {
      const s = document.createElement("span"); s.textContent = q;
      s.onclick = () => { inp.value = q; send(); };
      quick.appendChild(s);
    });
  }
  async function send() {
    const q = inp.value.trim(); if (!q) return;
    add(q, "me"); inp.value = "";
    const t = add("正在思考…", "bot");
    try {
      const r = await fetch(`${QA_API}/ask`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }), signal: AbortSignal.timeout(35000),
      });
      if (!r.ok) throw 0;
      const data = await r.json();
      t.textContent = data.answer || "（没有得到回答）";
    } catch (e) {
      t.textContent = "客服服务暂时不可用，请确认问答服务(:8125)已启动。";
    }
  }
  fab.onclick = () => { panel.classList.toggle("on"); if (panel.classList.contains("on")) { boot(); inp.focus(); } };
  panel.querySelector(".chat-close").onclick = () => panel.classList.remove("on");
  panel.querySelector("#chatSend").onclick = send;
  inp.onkeydown = e => { if (e.key === "Enter") send(); };
}
initChat();
updateCartBadge();
