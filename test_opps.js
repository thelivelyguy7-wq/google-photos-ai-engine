const fs = require('fs');
eval(fs.readFileSync('./site/site_data.js', 'utf8'));
const D = window.SITE_DATA;
const s0 = D.stage0;
const s1 = D.stage1;
const pct = (n, of) => (of ? ((100 * n) / of).toFixed(1) + "%" : "—");

try {
  const result = `<h1>Opportunities</h1>
  <p class="lede">Breaking down the business metric of successful retrieval into failure points, and identifying where the greatest opportunities exist.</p>

  <h2>Opportunity Areas</h2>
  <p class="muted">Using the decomposition above to identify where the greatest opportunities exist.</p>
  
  <div class="grid grid-2">
    <!-- Area 1: Context-to-Query Translation -->
    <div class="card" style="border-top: 4px solid var(--success);">
      <h3 style="margin-top:0;">1. Context-to-Query Translation</h3>
      <ul style="font-size: 14px; padding-left: 20px; line-height: 1.6;">
        <li style="margin-bottom: 8px;"><strong>Memory vs. Gap:</strong> The Insights data shows 200 records remember people and 134 remember visual appearance, but 199 explicitly lack precise time and 149 lack exact names.</li>
        <li style="margin-bottom: 8px;"><strong>Expression Barrier:</strong> The Evidence Explorer/Segments indicate ${s1.express_barrier} out of ${s0.relevant} (${pct(s1.express_barrier, s0.relevant)}%) state an explicit expression barrier where their memory couldn't be turned into a search keyword.</li>
        <li><strong>Impact:</strong> This directly addresses the 594 records identified in the Journey breakdown where users lacked specific memory information to form a traditional query.</li>
      </ul>
    </div>
    <!-- Area 2 -->
    <div class="card" style="border-top: 4px solid var(--warn);">
      <h3 style="margin-top:0;">2. Vague Query Interpretation</h3>
      <ul style="font-size: 14px; padding-left: 20px; line-height: 1.6;">
        <li style="margin-bottom: 8px;"><strong>Abandonment Rate:</strong> 341 records (42.6%) fall into SEG-1 (Exit-path retrievers), meaning their initial search failure led to complete abandonment (115 records) or failure (140 records).</li>
        <li style="margin-bottom: 8px;"><strong>Low Success Baseline:</strong> Only ${s1.outcome.found_quickly} out of ${s0.relevant} records (${pct(s1.outcome.found_quickly, s0.relevant)}%) were resolved on the "first attempt" (found quickly).</li>
        <li><strong>Impact:</strong> Improving the zero-state interpretation directly targets the 42.6% of users who hit a wall on query #1 and never recover.</li>
      </ul>
    </div>
  </div>`;
  console.log("SUCCESS, length:", result.length);
} catch (err) {
  console.error("FAILED:", err.stack);
}
