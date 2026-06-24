// 网关地址（Spring Cloud Gateway）。商品目录为公开接口，无需令牌；
// 登录后服务端签发的 JWT 存 localStorage，下单等敏感操作才需带 Authorization: Bearer。
const GATEWAY = "http://localhost:9000";

// 与 t_product 一致的兜底数据（网关未启动时用）；图标用 emoji 占位
const MOCK = [
  { id: 1, name: "小米 Redmi 手机 5G 全网通", price: 1000, emoji: "📱", sales: 8231, shop: "小米官方旗舰店" },
  { id: 2, name: "华为 HUAWEI Mate 旗舰手机", price: 2000, emoji: "📱", sales: 15600, shop: "华为官方旗舰店" },
  { id: 3, name: "Apple iPhone 苹果手机", price: 3000, emoji: "🍎", sales: 23400, shop: "Apple Store" },
  { id: 4, name: "OPPO Find 影像旗舰", price: 4000, emoji: "📱", sales: 6700, shop: "OPPO 官方旗舰店" },
  { id: 5, name: "小米平板 6 Pro 平板电脑", price: 2499, emoji: "💻", sales: 3400, shop: "小米官方旗舰店" },
  { id: 6, name: "华为 MatePad 二合一平板", price: 3299, emoji: "💻", sales: 2100, shop: "华为官方旗舰店" },
  { id: 7, name: "Apple Watch 智能手表", price: 2999, emoji: "⌚", sales: 9800, shop: "Apple Store" },
  { id: 8, name: "小米手环 8 运动监测", price: 239, emoji: "⌚", sales: 45000, shop: "小米官方旗舰店" },
  { id: 9, name: "华为 FreeBuds 无线耳机", price: 799, emoji: "🎧", sales: 12300, shop: "华为官方旗舰店" },
  { id: 10, name: "小米空气净化器 4", price: 999, emoji: "🌀", sales: 5600, shop: "小米官方旗舰店" },
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
      list.push({ id: p.id, name: p.name, price: p.price, emoji: m.emoji || "📦", sales: m.sales || 0, shop: m.shop || "官方旗舰店" });
    }
    // 真实只有4条，补充 mock 让首页更丰满
    return list.concat(MOCK.slice(4));
  } catch (e) {
    return MOCK; // 网关未启动 → 用兜底数据
  }
}

const PH = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="1"/><circle cx="8.5" cy="10" r="1.5"/><path d="M3 16l5-4 4 3 3-2 6 5"/></svg>';
function cardHTML(p) {
  return `<a class="card" href="#" onclick="return false">
    <div class="ph">${PH}</div>
    <div class="cname">${p.name}</div>
    <div class="cprice"><small>¥</small>${Number(p.price).toFixed(2)}</div>
    <div class="cmeta">${p.sales}+ 已售 · ${p.shop}</div></a>`;
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
function logout() { localStorage.removeItem("user"); renderUser(); }

// 统一的 Toast 提示（替代浏览器原生 alert）
function toast(msg, type) {
  const t = document.createElement("div");
  t.className = "toast" + (type === "error" ? " err" : "") + (type === "ok" ? " ok" : "");
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add("show"));
  setTimeout(() => { t.classList.remove("show"); setTimeout(() => t.remove(), 280); }, 2200);
}
