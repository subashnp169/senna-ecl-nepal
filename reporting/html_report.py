"""HTML report generator for ECL outputs."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List


def generate_html_report(results: List[Dict[str, Any]], totals: Dict[str, Any],
                         tenant_name: str = "Tenant", out_path: str = "report.html") -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    stage_rows = ""
    for s in ("stage1", "stage2", "stage3"):
        b = totals.get(s, {})
        stage_rows += (
            f"<tr><td>{s.replace('stage','Stage ')}</td>"
            f"<td>{b.get('count',0)}</td>"
            f"<td>{b.get('ead',0):,.2f}</td>"
            f"<td>{b.get('ecl',0):,.2f}</td>"
            f"<td>{b.get('coverage',0):.2f}%</td></tr>"
        )
    stage_rows += (
        f"<tr class='total'><td>TOTAL</td><td>{totals.get('count',0)}</td>"
        f"<td>{totals.get('total_ead',0):,.2f}</td>"
        f"<td>{totals.get('total_ecl',0):,.2f}</td>"
        f"<td>{totals.get('coverage',0):.2f}%</td></tr>"
    )

    detail_rows = ""
    for r in results[:500]:
        detail_rows += (
            f"<tr><td>{r.get('loan_name','')}</td><td>{r.get('stage','')}</td>"
            f"<td>{r.get('dpd','')}</td><td>{r.get('ead',0):,.2f}</td>"
            f"<td>{r.get('lgd',0):.4f}</td><td>{r.get('ecl_applied',0):,.2f}</td>"
            f"<td>{r.get('triggers','')}</td></tr>"
        )

    pc = totals.get("provision_comparison", {})
    pc_html = ""
    if pc:
        pc_html = f"""
        <h2>NRB Provision Comparison</h2>
        <table><tr><th>Metric</th><th>Value</th></tr>
        <tr><td>ECL</td><td>{pc.get('ecl',0):,.2f}</td></tr>
        <tr><td>Prudential</td><td>{pc.get('prudential',0):,.2f}</td></tr>
        <tr class='total'><td>Provision Required</td><td>{pc.get('provision_required',0):,.2f}</td></tr>
        </table>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{tenant_name} - ECL Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; color: #1E293B; background: #FFFFFF; }}
  h1 {{ color: #1F3864; }}
  h2 {{ color: #1F3864; margin-top: 24px; border-bottom: 2px solid #CBD5E8; padding-bottom: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }}
  th, td {{ border: 1px solid #CBD5E8; padding: 6px 8px; text-align: left; }}
  th {{ background: #1F3864; color: #FFFFFF; font-weight: 600; }}
  tr:nth-child(even) {{ background: #F5F7FA; }}
  tr.total {{ background: #E8EDF5; font-weight: 700; }}
  .meta {{ color: #64748B; font-size: 11px; margin-bottom: 16px; }}
  .badge {{ display: inline-block; background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
  .kpis {{ display: flex; gap: 16px; margin: 16px 0; }}
  .kpi {{ background: #F5F7FA; border-left: 4px solid #1F3864; padding: 10px 16px; border-radius: 6px; }}
  .kpi .label {{ font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700; }}
  .kpi .value {{ font-size: 18px; font-weight: 800; color: #1F3864; }}
  .triggers {{ font-size: 10px; color: #64748B; max-width: 300px; word-wrap: break-word; }}
</style>
</head>
<body>
  <h1>{tenant_name} — Expected Credit Loss Report</h1>
  <div class="meta">Generated: {datetime.now().isoformat()} &nbsp;|&nbsp; <span class="badge">PRELIMINARY / RESEARCH</span></div>

  <div class="kpis">
    <div class="kpi"><div class="label">Loans</div><div class="value">{totals.get('count',0)}</div></div>
    <div class="kpi"><div class="label">Total EAD</div><div class="value">{totals.get('total_ead',0):,.0f}</div></div>
    <div class="kpi"><div class="label">Total ECL</div><div class="value">{totals.get('total_ecl',0):,.0f}</div></div>
    <div class="kpi"><div class="label">Coverage</div><div class="value">{totals.get('coverage',0):.2f}%</div></div>
  </div>

  <h2>ECL Summary by Stage</h2>
  <table>
    <tr><th>Stage</th><th>Count</th><th>EAD</th><th>ECL</th><th>Coverage %</th></tr>
    {stage_rows}
  </table>

  {pc_html}

  <h2>Account-Level ECL Detail (first {min(len(results),500)} of {len(results)})</h2>
  <table>
    <tr><th>Account</th><th>Stage</th><th>DPD</th><th>EAD</th><th>LGD</th><th>ECL Applied</th><th>Triggers</th></tr>
    {detail_rows}
  </table>

  <p class="meta" style="margin-top:24px;">All outputs are PRELIMINARY/RESEARCH. Not approved for statutory booking.</p>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
