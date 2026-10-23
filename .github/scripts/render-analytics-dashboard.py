#!/usr/bin/env python3
"""Render a clean analytics-console SVG from metrics/history.json."""
from __future__ import annotations
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "metrics" / "history.json"
OUTPUT = ROOT / "assets" / "analytics-dashboard.svg"
OWNER = "sandeepmothukuri"
BG = "#07111f"
PANEL = "#0c1b2d"
LINE = "#173a55"
TEXT = "#e6f1ff"
MUTED = "#8ba7c2"
CYAN = "#35d6ff"
GREEN = "#54f0a2"
PURPLE = "#bd7bff"
ORANGE = "#ffad66"

def esc(value):
    return html.escape(str(value), quote=True)

def text(x, y, value, size=16, fill=TEXT, weight=400, anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(value)}</text>'

def rect(x, y, w, h, fill=PANEL, stroke=LINE, radius=16):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'

def card(x, y, w, label, value, detail, accent):
    return "\n".join([
        rect(x,y,w,112),
        f'<rect x="{x}" y="{y}" width="5" height="112" rx="2" fill="{accent}"/>',
        text(x+20,y+29,label.upper(),12,MUTED,700),
        text(x+20,y+66,value,28,accent,750),
        text(x+20,y+91,detail,11,MUTED,400),
    ])

def main():
    data = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {}
    profile = data.get("profile_views", [])
    repos = data.get("repos", {})
    today = dt.datetime.now(dt.timezone.utc).date()
    cutoff = today - dt.timedelta(days=29)

    def in_window(rows):
        out = []
        for row in rows:
            try:
                date = dt.date.fromisoformat(str(row.get("date", ""))[:10])
            except ValueError:
                continue
            if cutoff <= date <= today:
                out.append((date, row))
        return out

    profile_window = in_window(profile)
    profile_latest = profile[-1] if profile else {}
    profile_total = int(profile_latest.get("total", 0) or 0)
    profile_30d = sum(int(row.get("daily", 0) or 0) for _, row in profile_window)
    tracked = [(name, rows) for name, rows in repos.items() if rows]
    views_30d = sum(sum(int(row.get("views",0) or 0) for _,row in in_window(rows)) for _,rows in tracked)
    clones_30d = sum(sum(int(row.get("clones",0) or 0) for _,row in in_window(rows)) for _,rows in tracked)
    latest_rows = [rows[-1] for _, rows in tracked if rows]
    stars = sum(int(row.get("stars",0) or 0) for row in latest_rows)
    forks = sum(int(row.get("forks",0) or 0) for row in latest_rows)
    latest_date = max([str(profile_latest.get("date",""))] + [str(rows[-1].get("date","")) for _,rows in tracked if rows])
    latest_date = latest_date or "No snapshots yet"

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="790" viewBox="0 0 1200 790" role="img" aria-labelledby="title desc">',
        '<title id="title">Sandeep Mothukuri — Security Analytics Dashboard</title>',
        '<desc id="desc">Automatically generated dashboard using the repository metrics history. The metrics refresh with the GitHub Actions workflow.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07111f"/><stop offset="1" stop-color="#0a2033"/></linearGradient><linearGradient id="hero" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#102b46"/><stop offset="1" stop-color="#0b1828"/></linearGradient></defs>',
        '<rect width="1200" height="790" rx="24" fill="url(#bg)"/>',
        '<path d="M0 130 H1200" stroke="#173a55"/>',
        '<circle cx="1110" cy="40" r="100" fill="#0877a8" opacity=".08"/>',
        text(36,52,"SANDEEP MOTHUKURI",30,TEXT,800),
        text(37,82,"SECURITY ANALYTICS  /  SOC OPERATIONS  /  DETECTION ENGINEERING",13,CYAN,650),
        text(37,108,"Detect  ·  Investigate  ·  Hunt  ·  Respond",15,MUTED,400),
        '<circle cx="1108" cy="55" r="25" fill="#102d42" stroke="#35d6ff" stroke-width="1.5"/>',
        '<path d="M1097 55 l8 8 15 -18" fill="none" stroke="#35d6ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
        text(1157,52,"METRICS",11,MUTED,700,"end"),
        text(1157,72,"AUTO-REFRESH",11,GREEN,700,"end"),
        card(28,150,270,"PROFILE VIEWS",f"{profile_total:,}",f"{profile_30d:,} recorded in last 30 days",CYAN),
        card(312,150,270,"REPOSITORY VIEWS",f"{views_30d:,}", "Tracked repositories · last 30 days",GREEN),
        card(596,150,270,"REPOSITORY CLONES",f"{clones_30d:,}", "Tracked repositories · last 30 days",PURPLE),
        card(880,150,140,"TRACKED REPOS",f"{len(tracked):,}", "With history",ORANGE),
        card(1034,150,138,"STARS / FORKS",f"{stars:,} / {forks:,}", "Across tracked repos",CYAN),
        rect(28,282,700,270),
        text(52,316,"PROFILE VIEW TREND",16,TEXT,750),
        text(704,316,"DAILY SNAPSHOTS",10,MUTED,600,"end"),
    ]
    # Line chart from stored daily profile-view counts.
    chart_x, chart_y, chart_w, chart_h = 60, 350, 630, 150
    for i in range(4):
        y = chart_y + i * chart_h / 3
        svg.append(f'<line x1="{chart_x}" y1="{y:.1f}" x2="{chart_x+chart_w}" y2="{y:.1f}" stroke="{LINE}" stroke-dasharray="4 5"/>')
    values = [int(row.get("daily",0) or 0) for _,row in profile_window]
    if values:
        maxv = max(max(values),1)
        pts = []
        for i,v in enumerate(values):
            x = chart_x + (i/(max(len(values)-1,1)))*chart_w
            y = chart_y + chart_h - (v/maxv)*(chart_h-14)
            pts.append((x,y))
        pointstr = " ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
        svg.append(f'<polyline points="{pointstr}" fill="none" stroke="{CYAN}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        for x,y in pts[-8:]:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{CYAN}" stroke="{BG}" stroke-width="1.5"/>')
        svg.extend([text(chart_x,526,f"Daily profile-view delta · peak {maxv:,}",11,MUTED),text(chart_x+chart_w,526,f"{len(values)} daily records",11,MUTED,400,"end")])
    else:
        svg.append(text(60,420,"Waiting for profile-view snapshots",14,MUTED))
    # Top repositories chart, using tracked 30-day views and clones.
    svg.extend([rect(748,282,424,270),text(772,316,"REPOSITORY TRAFFIC",16,TEXT,750),text(1148,316,"LAST 30 DAYS",10,MUTED,600,"end")])
    ranked=[]
    for name,rows in tracked:
        win=[row for _,row in in_window(rows)]
        v=sum(int(r.get("views",0) or 0) for r in win)
        c=sum(int(r.get("clones",0) or 0) for r in win)
        ranked.append((v+c,name,v,c))
    ranked.sort(key=lambda item:(-item[0],item[1].lower()))
    top=ranked[:5]
    maxv=max([v+c for _,_,v,c in top] or [1]) or 1
    for i,(_,name,v,c) in enumerate(top):
        y=354+i*35
        svg.append(text(772,y+5,name[:26],11,TEXT,600))
        bar_x=970; bar_w=125
        svg.append(f'<rect x="{bar_x}" y="{y-9}" width="{bar_w}" height="12" rx="6" fill="#132c42"/>')
        svg.append(f'<rect x="{bar_x}" y="{y-9}" width="{max(2,bar_w*(v+c)/maxv):.1f}" height="12" rx="6" fill="{CYAN}"/>')
        svg.append(text(1148,y+5,f"{v}v · {c}c",10,MUTED,500,"end"))
    svg.extend([
        rect(28,572,560,166),
        text(52,606,"PORTFOLIO SIGNALS",16,TEXT,750),
        text(52,640,"30-day repository views + clones",12,MUTED),
        text(52,674,f"{views_30d:,} views",23,CYAN,750),
        text(310,674,f"{clones_30d:,} clones",23,GREEN,750),
        text(52,710,f"{len(tracked)} repositories have stored traffic history",11,MUTED),
        rect(608,572,564,166),
        text(632,606,"DATA FRESHNESS",16,TEXT,750),
        text(632,640,"Latest snapshot in history",12,MUTED),
        text(632,674,latest_date,24,PURPLE,750),
        text(632,710,"Traffic is sourced from stored GitHub API snapshots; zero means no recorded traffic.",10,MUTED),
        text(28,772,"SIEM  ·  INCIDENT RESPONSE  ·  THREAT HUNTING  ·  OPEN-SOURCE LABS",11,MUTED,650),
        text(1172,772,"GENERATED BY GITHUB ACTIONS",10,CYAN,650,"end"),
        '</svg>'
    ])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(svg), encoding="utf-8")
    print(f"Rendered {OUTPUT} from {latest_date}; tracked repositories={len(tracked)}")

if __name__ == "__main__":
    main()
