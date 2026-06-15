from __future__ import annotations

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Agent Observability Dashboard</title>
  <style>
    :root { color-scheme: dark; --bg:#07111f; --panel:#101e31; --line:#29405d; --text:#edf5ff; --muted:#91a4ba; --good:#42d6a4; --bad:#ff6b7a; --accent:#6eb4ff; }
    * { box-sizing:border-box } body { margin:0; min-height:100vh; font-family:Segoe UI,Arial,sans-serif; background:radial-gradient(circle at top right,#17345d 0,#07111f 45%); color:var(--text); padding:28px }
    header { display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:22px } h1 { margin:0; font-size:30px } .subtitle,.meta { color:var(--muted) } .meta { text-align:right; font-size:13px }
    .grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px } .card { background:linear-gradient(145deg,rgba(20,38,62,.96),rgba(12,26,44,.96)); border:1px solid var(--line); border-radius:16px; padding:18px; min-height:190px; box-shadow:0 12px 30px rgba(0,0,0,.2) }
    .label { color:#b8c9dc; font-size:14px; text-transform:uppercase; letter-spacing:.08em } .value { font-size:30px; font-weight:700; margin:12px 0 2px } .unit { color:var(--muted); font-size:13px } .threshold { margin-top:10px; color:var(--muted); font-size:12px } .good { color:var(--good) } .bad { color:var(--bad) }
    svg { width:100%; height:54px; margin-top:16px; overflow:visible } polyline { fill:none; stroke:var(--accent); stroke-width:2.5; vector-effect:non-scaling-stroke } .baseline { stroke:#405a78; stroke-width:1; stroke-dasharray:4 4 }
    .alerts { margin-top:18px; display:flex; gap:10px; flex-wrap:wrap } .alert { border:1px solid var(--line); border-radius:999px; padding:7px 11px; color:var(--muted); font-size:12px } .alert.firing { color:#fff; border-color:var(--bad); background:rgba(255,107,122,.15) }
    @media (max-width:900px) { .grid { grid-template-columns:1fr 1fr } } @media (max-width:600px) { body { padding:16px } header { align-items:start; flex-direction:column } .meta { text-align:left } .grid { grid-template-columns:1fr } }
  </style>
</head>
<body>
  <header><div><h1>Agent Observability</h1><div class="subtitle">Layer 2 dashboard: service health and AI workload signals</div></div><div class="meta">Time range: last 1 hour<br>Auto refresh: 15 seconds<br><span id="updated">Waiting for metrics</span></div></header>
  <main class="grid">
    <section class="card"><div class="label">Latency P50 / P95 / P99</div><div id="latency" class="value">0 / 0 / 0</div><div class="unit">milliseconds</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"><line class="baseline" x1="0" y1="35" x2="100" y2="35"/><polyline id="latency-chart" points="0,40 100,40"/></svg><div class="threshold">SLO: P95 &lt; 3000 ms</div></section>
    <section class="card"><div class="label">Traffic</div><div id="traffic" class="value">0</div><div class="unit">requests total / requests per minute</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"><line class="baseline" x1="0" y1="35" x2="100" y2="35"/><polyline id="traffic-chart" points="0,40 100,40"/></svg><div class="threshold">Operational signal: request volume</div></section>
    <section class="card"><div class="label">Error rate</div><div id="errors" class="value good">0%</div><div id="error-breakdown" class="unit">No errors</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"><line class="baseline" x1="0" y1="35" x2="100" y2="35"/><polyline id="error-chart" points="0,40 100,40"/></svg><div class="threshold">SLO: error rate &lt; 2%</div></section>
    <section class="card"><div class="label">Cost over time</div><div id="cost" class="value">$0.000000</div><div class="unit">USD total / maximum per request</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"><line class="baseline" x1="0" y1="35" x2="100" y2="35"/><polyline id="cost-chart" points="0,40 100,40"/></svg><div class="threshold">Budget: &lt; $2.50 per day</div></section>
    <section class="card"><div class="label">Tokens in / out</div><div id="tokens" class="value">0 / 0</div><div class="unit">tokens</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"><line class="baseline" x1="0" y1="35" x2="100" y2="35"/><polyline id="tokens-chart" points="0,40 100,40"/></svg><div class="threshold">Watch output-token growth for cost spikes</div></section>
    <section class="card"><div class="label">Quality proxy</div><div id="quality" class="value">0.00</div><div class="unit">average heuristic score</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"><line class="baseline" x1="0" y1="35" x2="100" y2="35"/><polyline id="quality-chart" points="0,40 100,40"/></svg><div class="threshold">Target: average quality >= 0.75</div></section>
  </main>
  <div id="alerts" class="alerts"></div>
  <script>
    function points(values) { if (!values.length) return '0,40 100,40'; const max=Math.max(...values,1); return values.map((v,i)=>`${values.length===1?50:i*100/(values.length-1)},${38-v/max*34}`).join(' ') }
    function chart(id, values) { document.getElementById(id).setAttribute('points', points(values)) }
    async function refresh() {
      const [m,a]=await Promise.all([fetch('/metrics').then(r=>r.json()),fetch('/alerts').then(r=>r.json())]); const series=m.time_series||[];
      latency.textContent=`${m.latency_p50_ms} / ${m.latency_p95_ms} / ${m.latency_p99_ms}`; traffic.textContent=`${m.traffic} / ${m.requests_per_minute}`;
      errors.textContent=`${m.error_rate_pct}%`; errors.className=`value ${m.error_rate_pct>2?'bad':'good'}`; document.getElementById('error-breakdown').textContent=Object.keys(m.error_breakdown).length?JSON.stringify(m.error_breakdown):'No errors';
      cost.textContent=`$${m.total_cost_usd.toFixed(6)} / $${m.max_cost_usd.toFixed(6)}`; tokens.textContent=`${m.tokens_in_total} / ${m.tokens_out_total}`;
      quality.textContent=m.quality_avg.toFixed(2); quality.className=`value ${m.quality_avg>=.75?'good':'bad'}`;
      chart('latency-chart',series.map(x=>x.latency_ms)); chart('traffic-chart',series.map((_,i)=>i+1)); chart('error-chart',series.map(x=>x.error?1:0)); chart('cost-chart',series.map(x=>x.cost_usd)); chart('tokens-chart',series.map(x=>x.tokens_in+x.tokens_out)); chart('quality-chart',series.map(x=>x.quality_score));
      alerts.innerHTML=a.map(x=>`<a href="${x.runbook}" class="alert ${x.firing?'firing':''}">${x.severity} ${x.name}: ${x.firing?'FIRING':'OK'}</a>`).join(''); updated.textContent=`Updated ${new Date().toLocaleTimeString()}`;
    }
    refresh().catch(console.error); setInterval(()=>refresh().catch(console.error),15000);
  </script>
</body>
</html>"""


RUNBOOK_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Alert Runbooks</title>
<style>body{font:16px Segoe UI,Arial;background:#07111f;color:#edf5ff;max-width:900px;margin:auto;padding:32px}section{background:#101e31;border:1px solid #29405d;border-radius:14px;padding:20px;margin:16px 0}code{color:#6eb4ff}a{color:#6eb4ff}</style></head><body>
<h1>Alert Runbooks</h1><p><a href="/">Back to dashboard</a></p>
<section id="high-latency-p95"><h2>High latency P95 (P2)</h2><p>Trigger: <code>latency_p95_ms &gt; 3000 for 5m</code></p><p>Inspect slow traces, compare RAG and LLM spans, then check <code>rag_slow</code>. Disable the incident, use a retrieval timeout, or route to a fallback source.</p></section>
<section id="high-error-rate"><h2>High error rate (P1)</h2><p>Trigger: <code>error_rate_pct &gt; 5 for 5m</code></p><p>Group logs by error type, inspect failed traces, and disable the failing tool or use a fallback.</p></section>
<section id="cost-budget-spike"><h2>Cost budget spike (P2)</h2><p>Trigger: <code>max_cost_usd &gt; 0.005 for 1m</code></p><p>Compare output tokens by trace and feature, then shorten prompts, cap output tokens, or route to a cheaper model.</p></section>
</body></html>"""