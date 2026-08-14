window.API = {
  search: q => fetch(`/api/search?q=${encodeURIComponent(q)}`).then(r => r.json()),
  stock: code => fetch(`/api/stock/${encodeURIComponent(code)}`).then(r => r.json()),
  basic: code => fetch(`/api/stock/${encodeURIComponent(code)}/basic`).then(r => r.json()),
  module: (code, module) => fetch(`/api/stock/${encodeURIComponent(code)}/module/${module}`).then(async r => {
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || '请求失败');
    return data;
  })
};
