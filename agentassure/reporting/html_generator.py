"""Client-Ready HTML Dashboard Generator for Quality Reporting."""

from agentassure.schemas.reporting import QualityReportResponse


class HTMLReportGenerator:
    """Renders responsive, self-contained HTML executive quality dashboards."""

    @classmethod
    def render(cls, report: QualityReportResponse) -> str:
        """Produce an HTML5 document containing KPIs, bar charts, and impact metrics."""
        category_rows = "".join(
            f"<tr><td style='padding:8px;border-bottom:1px solid #e2e8f0;'><strong>{cat}</strong></td>"
            f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;text-align:right;'>{cnt}</td></tr>"
            for cat, cnt in report.failure_distribution_by_category.items()
        )

        impact_rows = "".join(
            f"<tr><td style='padding:8px;border-bottom:1px solid #e2e8f0;'><code>{item['ticket_id']}</code></td>"
            f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;'>{item['title']}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;text-align:right;'>{item['failure_rate_before']:.1f}% → {item['failure_rate_after']:.1f}%</td>"
            f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;'><strong>-{item['reduction_percent']:.1f}%</strong></td></tr>"
            for item in report.before_after_fix_impact
        ) or "<tr><td colspan='4' style='padding:12px;text-align:center;color:#64748b;'>No post-release verified tickets yet.</td></tr>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AgentAssure Quality & Regression Report ({report.report_date})</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .header {{ background: #0f172a; color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .kpi-title {{ font-size: 13px; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }}
    .kpi-value {{ font-size: 28px; font-weight: bold; color: #0f172a; }}
    .section {{ background: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: #f1f5f9; padding: 10px; text-align: left; font-size: 13px; color: #475569; }}
    .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; background: #e0f2fe; color: #0369a1; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 style="margin: 0 0 8px 0;">🛡️ AgentAssure QA & Closed-Loop Quality Report</h1>
      <p style="margin: 0; color: #94a3b8;">Generated on {report.report_date} | Active Rubric: <span class="badge">{report.active_rubric_version}</span></p>
    </div>

    <div class="grid">
      <div class="card">
        <div class="kpi-title">Reviewed Conversations</div>
        <div class="kpi-value">{report.reviewed_conversations} / {report.total_conversations}</div>
      </div>
      <div class="card">
        <div class="kpi-title">Coverage Ratio</div>
        <div class="kpi-value">{report.conversation_coverage_pct}%</div>
      </div>
      <div class="card">
        <div class="kpi-title">Review SLA Compliance</div>
        <div class="kpi-value">{report.review_sla_compliance_pct}%</div>
      </div>
      <div class="card">
        <div class="kpi-title">Inter-Rater Kappa</div>
        <div class="kpi-value">{report.inter_rater_kappa_overall:.2f}</div>
      </div>
    </div>

    <div class="section">
      <h3 style="margin-top:0;">Confirmed Failures by Category</h3>
      <table>
        <thead>
          <tr>
            <th>Taxonomy Category (L1)</th>
            <th style="text-align:right;">Incident Count</th>
          </tr>
        </thead>
        <tbody>
          {category_rows or "<tr><td colspan='2' style='padding:12px;text-align:center;'>No failures logged.</td></tr>"}
        </tbody>
      </table>
    </div>

    <div class="section">
      <h3 style="margin-top:0;">Closed-Loop Fix Impact (Before vs. After Release)</h3>
      <table>
        <thead>
          <tr>
            <th>Ticket ID</th>
            <th>Issue Title</th>
            <th style="text-align:right;">Failure Rate Shift</th>
            <th style="text-align:right;">Defect Reduction</th>
          </tr>
        </thead>
        <tbody>
          {impact_rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>"""
