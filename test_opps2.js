const fs = require('fs');
global.window = {};
eval(fs.readFileSync('./site/site_data.js', 'utf8'));
const D = window.SITE_DATA;
const s0 = D.stage0;
const s1 = D.stage1;
const pct = (n, of) => (of ? ((100 * n) / of).toFixed(1) + '%' : '—');
try {
    const res = `${s1.express_barrier} ${s0.relevant} ${pct(s1.express_barrier, s0.relevant)} ${s1.outcome.found_quickly} ${pct(s1.outcome.found_quickly, s0.relevant)}`;
    console.log("SUCCESS:", res);
} catch (e) {
    console.error("ERROR:", e.stack);
}
