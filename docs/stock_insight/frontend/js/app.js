const MODULES = [
  ['overview','总览'],['market','行情'],['finance','财务'],['valuation','估值'],['industry','行业'],
  ['etf','ETF'],['index','指数'],['news','新闻'],['notice','公告'],['shareholder','股东'],
  ['dividend','分红'],['business','业务'],['events','事件'],['risk','风险'],['ai','AI分析']
];
let currentCode = null;
let loadedModules = new Set();

const $ = id => document.getElementById(id);

function fmt(v){
  if(v === null || v === undefined) return '-';
  if(typeof v === 'number') return v.toLocaleString('zh-CN');
  return v;
}
function money(v){
  if(typeof v !== 'number') return fmt(v);
  if(Math.abs(v) >= 1e12) return (v/1e12).toFixed(2)+' 万亿';
  if(Math.abs(v) >= 1e8) return (v/1e8).toFixed(2)+' 亿';
  if(Math.abs(v) >= 1e4) return (v/1e4).toFixed(2)+' 万';
  return fmt(v);
}
function esc(x){return String(x ?? '').replace(/[&<>\"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\':'&#92;','"':'&quot;'}[s]));}

function createTabs(){
  $('tabbar').innerHTML = MODULES.map(([key,label],i)=>`<button class="tab ${i===0?'active':''}" data-module="${key}">${label}</button>`).join('');
  document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>openModule(btn.dataset.module)));
}

async function openStock(code){
  currentCode = code; loadedModules = new Set();
  const stock = await API.stock(code);
  $('emptyState').hidden = true; $('stockPage').hidden = false;
  $('stockName').textContent = stock.name;
  $('stockCode').textContent = stock.code;
  $('stockSub').textContent = `${stock.full_name} · ${stock.market} · ${stock.board} · ${stock.industry}`;
  $('stockPrice').textContent = Number(stock.price).toFixed(2);
  $('stockChange').textContent = `${stock.change >= 0 ? '+' : ''}${stock.change}%`;
  $('stockChange').style.color = stock.change >= 0 ? 'var(--green)' : 'var(--red)';
  $('summaryCards').innerHTML = [
    ['总市值',money(stock.market_cap)],['流通市值',money(stock.float_market_cap)],['PE-TTM',stock.pe_ttm],
    ['动态PE',stock.pe_dynamic],['PB',stock.pb],['股息率',stock.dividend_yield+'%'],['ROE',stock.roe+'%'],['营收增速',stock.revenue_yoy+'%']
  ].map(([l,v])=>`<div class="metric"><div class="label">${l}</div><div class="value">${fmt(v)}</div></div>`).join('');
  createTabs();
  await openModule('overview');
}

function renderKv(obj){
  return Object.entries(obj||{}).map(([k,v])=>`<div class="kv"><span class="k">${esc(k)}</span><span>${esc(fmt(v))}</span></div>`).join('');
}
function card(title, html){return `<div class="module-card"><h3>${title}</h3>${html}</div>`;}
function tableFromRows(rows,headers){
  return `<table><thead><tr>${headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${esc(fmt(c))}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

function render(module,payload){
  const d = payload.data || {};
  if(module==='overview') return `<div class="section-grid">
    ${card('核心指标',renderKv(d.cards))}
    ${card('当前公司',renderKv({名称:$('stockName').textContent,代码:$('stockCode').textContent,状态:'Mock数据'}))}
    ${card('研究模块',renderKv({'财务':'已预留','估值':'已预留','行业':'已预留','ETF':'已预留','新闻':'已预留'}))}
    ${card('近期重点', (d.highlights||[]).map(x=>`<div class="tag">${esc(x)}</div>`).join(''))}
  </div>`;
  if(module==='market') return `<div class="section-grid">
    ${card('行情',renderKv(d.quote))}
    ${card('技术指标',(d.technical||[]).map(x=>`<span class="tag">${x}</span>`).join(''))}
  </div><div class="table-card"><h3>价格数据占位</h3>${tableFromRows((d.chart||[]).map(x=>[x.date,x.price]),['时间','价格'])}</div>`;
  if(module==='finance') return `<div class="section-grid">${card('利润表核心',renderKv(d.income))}${card('财务质量',renderKv(d.quality))}</div><div class="table-card"><h3>财务报表</h3><div class="placeholder">后续接入资产负债表、现金流量表、季度/年度历史数据。</div></div>`;
  if(module==='valuation') return `<div class="section-grid">${card('当前估值',renderKv(d.current))}${card('历史估值',renderKv(d.history))}</div><div class="table-card"><h3>估值趋势</h3><div class="placeholder">后续接入 PE/PB/PS 历史序列、分位数和行业对比。</div></div>`;
  if(module==='industry') return `<div class="section-grid">${card('行业分类',renderKv(d.classifications))}${card('行业对比',(d.comparison||[]).map(x=>`<div class="tag">${x}</div>`).join(''))}</div>`;
  if(module==='etf' || module==='index' || module==='news' || module==='notice') return `<div class="table-card"><h3>${MODULES.find(x=>x[0]===module)[1]}</h3><div class="placeholder">${esc(d.note || '暂无数据。当前页面只搭建结构，后续在此模块接入真实数据。')}</div></div>`;
  if(module==='shareholder') return `<div class="section-grid">${card('十大股东',`<div class="placeholder">${esc(d.note)}</div>`)}${card('机构持仓',`<div class="placeholder">后续接入基金、社保、QFII、北向等。</div>`)}</div>`;
  if(module==='dividend') return `<div class="section-grid">${card('分红统计',renderKv(d.stats))}</div><div class="table-card"><h3>历史分红</h3><div class="placeholder">后续接入分红历史、除权除息日、股息率。</div></div>`;
  if(module==='business') return `<div class="section-grid">${card('主营业务',(d.main||[]).map(x=>`<div class="tag">${esc(x)}</div>`).join(''))}${card('业务结构',`<div class="placeholder">后续接入产品、地区、客户、收入与利润结构。</div>`)}</div>`;
  if(module==='events') return `<div class="table-card"><h3>公司事件时间轴</h3><div class="timeline"><div class="placeholder">暂无事件，后续接入公告、合同、回购、增持、并购等事件。</div></div></div>`;
  if(module==='risk') return `<div class="table-card"><h3>风险因素</h3>${(d.items||[]).map(x=>`<div class="kv"><span>${esc(x)}</span><span>待接入</span></div>`).join('')}</div>`;
  if(module==='ai') return `<div class="section-grid">${card('公司画像',`<p>${esc(d.company_profile)}</p>`)}${card('成长逻辑',`<p>${esc(d.growth_logic)}</p>`)}${card('催化剂',`<div class="placeholder">AI分析接口预留</div>`)}${card('风险与关注点',`<div class="placeholder">AI分析接口预留</div>`)}</div>`;
  return `<div class="table-card"><div class="placeholder">模块暂未实现</div></div>`;
}

async function openModule(module){
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.module===module));
  $('moduleContent').innerHTML = `<div class="table-card"><div class="placeholder">正在加载 ${module} ...</div></div>`;
  try{
    const payload = await API.module(currentCode,module);
    loadedModules.add(module);
    $('moduleContent').innerHTML = render(module,payload);
  }catch(e){
    $('moduleContent').innerHTML = `<div class="table-card"><div class="placeholder">加载失败：${esc(e.message)}</div></div>`;
  }
}

async function doSearch(){
  const q = $('searchInput').value.trim(); if(!q) return;
  const list = await API.search(q);
  if(list.length===1){ $('searchDropdown').innerHTML=''; openStock(list[0].code); return; }
  $('searchDropdown').innerHTML = list.map(x=>`<div class="search-item" data-code="${x.code}"><b>${esc(x.name)}</b>　${esc(x.code)}　<span class="muted">${esc(x.industry)}</span></div>`).join('');
  document.querySelectorAll('.search-item').forEach(i=>i.addEventListener('click',()=>{ $('searchDropdown').innerHTML=''; openStock(i.dataset.code); }));
}

$('searchBtn').addEventListener('click',doSearch);
$('searchInput').addEventListener('keydown',e=>{if(e.key==='Enter')doSearch()});
$('searchInput').addEventListener('input',()=>{if(!$('searchInput').value.trim()) $('searchDropdown').innerHTML='';});
document.querySelectorAll('.examples button').forEach(b=>b.addEventListener('click',()=>openStock(b.dataset.code)));
