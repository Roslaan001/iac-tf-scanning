#!/usr/bin/env python3
"""
Convert Checkov JSON output to a modern, self-contained interactive HTML report.
Usage:
    python3 scripts/generate_checkov_html.py checkov-report.json checkov-terraform-report.html
"""

import json
import sys
import html
import os

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkov IaC Security & Compliance Report</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --critical: #ef4444;
            --high: #f97316;
            --medium: #f59e0b;
            --low: #3b82f6;
            --passed: #10b981;
            --code-bg: #0b0f19;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            padding: 30px 20px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            padding-bottom: 25px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }}
        .header-title h1 {{
            font-size: 28px;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .header-title p {{
            color: var(--text-muted);
            margin-top: 6px;
            font-size: 14px;
        }}
        .badge-framework {{
            background: #1e293b;
            color: var(--primary);
            border: 1px solid #38bdf840;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .stat-label {{
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: var(--text-muted);
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 700;
        }}
        .stat-passed {{ color: var(--passed); }}
        .stat-failed {{ color: var(--critical); }}
        .stat-total {{ color: var(--primary); }}
        .stat-skipped {{ color: var(--medium); }}

        .controls {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 25px;
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: center;
            justify-content: space-between;
        }}
        .search-box {{
            flex: 1;
            min-width: 250px;
        }}
        .search-box input {{
            width: 100%;
            padding: 10px 14px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-main);
            font-size: 14px;
            outline: none;
        }}
        .search-box input:focus {{
            border-color: var(--primary);
        }}
        .filter-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            background: var(--bg);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--surface-hover);
            color: var(--text-main);
            border-color: var(--primary);
        }}

        .results-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .check-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            transition: border-color 0.2s ease;
        }}
        .check-card.FAILED {{
            border-left: 5px solid var(--critical);
        }}
        .check-card.PASSED {{
            border-left: 5px solid var(--passed);
        }}
        .check-header {{
            padding: 16px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            user-select: none;
        }}
        .check-header:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .check-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 6px;
        }}
        .status-badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .status-failed {{ background: #ef444420; color: var(--critical); border: 1px solid #ef444440; }}
        .status-passed {{ background: #10b98120; color: var(--passed); border: 1px solid #10b98140; }}
        
        .check-id {{
            font-family: monospace;
            font-size: 12px;
            color: var(--primary);
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #334155;
        }}
        .check-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text-main);
        }}
        .check-target {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
            font-family: monospace;
        }}
        .chevron {{
            font-size: 18px;
            color: var(--text-muted);
            transition: transform 0.2s ease;
        }}
        .check-card.open .chevron {{
            transform: rotate(180deg);
        }}
        .check-body {{
            display: none;
            padding: 20px;
            border-top: 1px solid var(--border);
            background: rgba(11, 15, 25, 0.5);
        }}
        .check-card.open .check-body {{
            display: block;
        }}
        .detail-row {{
            margin-bottom: 12px;
            font-size: 13px;
        }}
        .detail-label {{
            color: var(--text-muted);
            font-weight: 600;
            display: inline-block;
            width: 120px;
        }}
        .detail-value {{
            color: var(--text-main);
            font-family: monospace;
        }}
        .code-container {{
            margin-top: 14px;
            background: var(--code-bg);
            border: 1px solid #1e293b;
            border-radius: 8px;
            overflow-x: auto;
            padding: 12px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
            line-height: 1.6;
        }}
        .code-line {{
            display: flex;
            gap: 16px;
        }}
        .line-num {{
            color: #64748b;
            user-select: none;
            min-width: 32px;
            text-align: right;
        }}
        .line-text {{
            color: #e2e8f0;
            white-space: pre;
        }}
        .guideline-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: var(--primary);
            text-decoration: none;
            font-size: 13px;
            margin-top: 10px;
            font-weight: 500;
        }}
        .guideline-link:hover {{
            text-decoration: underline;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">
                <h1>🛡️ Checkov IaC Security & Compliance Report</h1>
                <p>Automated policy-as-code and CIS benchmark inspection for Terraform</p>
            </div>
            <div>
                <span class="badge-framework">Terraform Scanner</span>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Checks</div>
                <div class="stat-value stat-total">{total}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed Checks</div>
                <div class="stat-value stat-failed">{failed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Passed Checks</div>
                <div class="stat-value stat-passed">{passed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Skipped Checks</div>
                <div class="stat-value stat-skipped">{skipped}</div>
            </div>
        </div>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search by Check ID, resource, rule, or file..." oninput="filterCards()">
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="setFilter('ALL', this)">All ({total})</button>
                <button class="filter-btn" onclick="setFilter('FAILED', this)">Failed ({failed})</button>
                <button class="filter-btn" onclick="setFilter('PASSED', this)">Passed ({passed})</button>
            </div>
        </div>

        <div class="results-list" id="resultsList">
            {cards}
        </div>

        <footer>
            Generated automatically by Checkov IaC Security Pipeline
        </footer>
    </div>

    <script>
        let currentStatusFilter = 'ALL';

        function toggleCard(header) {{
            const card = header.parentElement;
            card.classList.toggle('open');
        }}

        function setFilter(status, btn) {{
            currentStatusFilter = status;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterCards();
        }}

        function filterCards() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.check-card');

            cards.forEach(card => {{
                const status = card.dataset.status;
                const text = card.dataset.search;

                const matchesStatus = (currentStatusFilter === 'ALL' || status === currentStatusFilter);
                const matchesQuery = !query || text.includes(query);

                if (matchesStatus && matchesQuery) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

def generate_card(check, status):
    check_id = html.escape(str(check.get("check_id", "N/A")))
    check_name = html.escape(str(check.get("check_name", "Unknown Check")))
    resource = html.escape(str(check.get("resource", "N/A")))
    file_path = html.escape(str(check.get("file_path", "N/A")))
    file_lines = check.get("file_line_range", [1, 1])
    guideline = check.get("guideline") or ""

    code_lines_html = []
    code_block = check.get("code_block", [])
    if code_block:
        for item in code_block:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                ln, code = item
                code_lines_html.append(
                    f'<div class="code-line"><span class="line-num">{ln}</span><span class="line-text">{html.escape(code.rstrip())}</span></div>'
                )
    
    code_html = f'<div class="code-container">{"".join(code_lines_html)}</div>' if code_lines_html else ""
    guideline_html = f'<div style="margin-top: 12px;"><a class="guideline-link" href="{html.escape(guideline)}" target="_blank" rel="noopener noreferrer">📖 Remediation Guideline & Documentation &rarr;</a></div>' if guideline else ""

    status_class = "status-failed" if status == "FAILED" else "status-passed"

    search_data = f"{check_id} {check_name} {resource} {file_path}".lower()

    return f"""
    <div class="check-card {status}" data-status="{status}" data-search="{html.escape(search_data)}">
        <div class="check-header" onclick="toggleCard(this)">
            <div>
                <div class="check-meta">
                    <span class="status-badge {status_class}">{status}</span>
                    <span class="check-id">{check_id}</span>
                </div>
                <div class="check-title">{check_name}</div>
                <div class="check-target">{resource} &bull; {file_path}:{file_lines[0]}-{file_lines[1]}</div>
            </div>
            <div class="chevron">&#9662;</div>
        </div>
        <div class="check-body">
            <div class="detail-row"><span class="detail-label">Resource:</span><span class="detail-value">{resource}</span></div>
            <div class="detail-row"><span class="detail-label">File:</span><span class="detail-value">{file_path} (lines {file_lines[0]}-{file_lines[1]})</span></div>
            {code_html}
            {guideline_html}
        </div>
    </div>
    """

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate_checkov_html.py <input.json> <output.html>")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Checkov output can be a dict or a list of dicts (for multi-framework scans)
    if isinstance(data, dict):
        reports = [data]
    elif isinstance(data, list):
        reports = data
    else:
        reports = []

    passed_checks = []
    failed_checks = []
    skipped_checks = []

    for report in reports:
        results = report.get("results", {})
        passed_checks.extend(results.get("passed_checks", []))
        failed_checks.extend(results.get("failed_checks", []))
        skipped_checks.extend(results.get("skipped_checks", []))

    total_passed = len(passed_checks)
    total_failed = len(failed_checks)
    total_skipped = len(skipped_checks)
    total_count = total_passed + total_failed + total_skipped

    cards_html = []

    # Display failed checks first, then passed
    for c in failed_checks:
        cards_html.append(generate_card(c, "FAILED"))
    for c in passed_checks:
        cards_html.append(generate_card(c, "PASSED"))

    rendered = HTML_TEMPLATE.format(
        total=total_count,
        passed=total_passed,
        failed=total_failed,
        skipped=total_skipped,
        cards="".join(cards_html)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"Successfully generated Checkov HTML report: {output_path}")

if __name__ == "__main__":
    main()
