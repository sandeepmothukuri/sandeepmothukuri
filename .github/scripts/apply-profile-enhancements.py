#!/usr/bin/env python3
from pathlib import Path

README = Path("README.md")
text = README.read_text(encoding="utf-8")

# Keep the current automated status block, but remove the stale UK timestamp.
text = text.replace(
    'https://img.shields.io/badge/Status-%F0%9F%9B%8C%20Weekend%20%C2%B7%20UK%2022%3A24%20BST-8b949e?style=flat-square&labelColor=132f4c',
    'https://img.shields.io/badge/Status-%F0%9F%9B%8C%20Weekend%20%C2%B7%20India%20IST-8b949e?style=flat-square&labelColor=132f4c',
)
text = text.replace(
    'alt="Status: 🛌 Weekend · UK 22:24 BST"',
    'alt="Status: 🛌 Weekend · India IST"',
)

# Automated portfolio sections. Markers make this idempotent and safe for future runs.
top_repos = '''\n## 🏆 Top Repositories — Last 30 Days\n\n> Automatically ranked daily using repository traffic: **views + clones**, with stars and forks shown for additional context.\n\n<!-- TOP-REPOS START -->\n\n| Rank | Repository | Views | Clones | Stars | Forks |\n|---|---|---:|---:|---:|---:|\n| 🥇 | **Enterprise-Detection-Engineering-SOC-Lab** | — | — | — | — |\n| 🥈 | **AI-Augmented-SOC-Lab** | — | — | — | — |\n| 🥉 | **PromptShield** | — | — | — | — |\n\n<!-- TOP-REPOS END -->\n\n> 🔄 This section is automatically recalculated from the latest repository traffic history.\n'''

focus = '''\n## 🎯 Security Engineering Focus\n\n| Domain | Focus |\n|---|---|\n| 🔎 **Detection Engineering** | Sigma · KQL · SPL · MITRE ATT&CK · Detection-as-Code |\n| 🛡️ **SOC Operations** | L2/L3 triage · Incident Response · Threat Hunting · RCA |\n| 🤖 **AI Security** | LLM Security · Prompt Injection · AI-assisted SOC · AI Firewall |\n| ⚙️ **Security Automation** | Python · PowerShell · SOAR · CI/CD · Automated Enrichment |\n| ☁️ **Cloud Security** | Microsoft Defender · Sentinel · Azure · AWS |\n| 🧪 **Adversary Simulation** | MITRE ATT&CK · Caldera · Atomic Red Team |\n'''

projects = '''\n## 🧩 Projects → Capabilities\n\n| Project | Demonstrates |\n|---|---|\n| 🔥 [SOCForge](https://github.com/sandeepmothukuri/socforge) | SOC triage · investigation · detection engineering · AI-assisted security operations |\n| 🤖 [AI-SOC-Decision-Engine](https://github.com/sandeepmothukuri/AI-SOC-Decision-Engine) | AI-assisted SOC decisioning · evidence analysis · risk assessment |\n| 🛡️ [PromptShield](https://github.com/sandeepmothukuri/PromptShield) | Prompt injection defense · LLM security · AI application protection |\n| 🛡️ [PromptSentinel](https://github.com/sandeepmothukuri/PromptSentinel) | AI firewall · prompt injection detection · SARIF/SIEM integration |\n| 🧠 [AI-Augmented-SOC-Lab](https://github.com/sandeepmothukuri/AI-Augmented-SOC-Lab) | AI SOC experimentation · detection engineering · threat hunting |\n| 🎯 [sentinel-detection-engine](https://github.com/sandeepmothukuri/sentinel-detection-engine) | KQL · Microsoft Sentinel · MITRE ATT&CK · detection-as-code |\n'''

principles = '''\n## 🏗️ Engineering Principles\n\n`Detection-as-Code` · `Evidence-Driven Investigation` · `Automation-First SOC` · `MITRE ATT&CK Mapping` · `Reproducible Security Labs` · `AI-Assisted Analysis` · `CI/CD Validation` · `Measurable MTTD / MTTR Reduction`\n'''

# Remove previously generated sections before reinserting them, preventing duplicates.
for start, end in [
    ("<!-- TOP-REPOS START -->", "<!-- TOP-REPOS END -->"),
    ("## 🎯 Security Engineering Focus", "## 🧩 Projects → Capabilities"),
    ("## 🧩 Projects → Capabilities", "## 🏗️ Engineering Principles"),
]:
    if start in text:
        a = text.index(start)
        if start.startswith("<!--"):
            a = text.rfind("## 🏆 Top Repositories", 0, a)
        b = text.index(end, a) + len(end)
        text = text[:a].rstrip() + "\n\n" + text[b:].lstrip()

# Insert portfolio sections after Currently focused, before Ask me about.
anchor = "## 💬 Ask me about"
if anchor in text:
    block = top_repos + focus + projects + principles + "\n"
    text = text.replace(anchor, block + anchor, 1)

README.write_text(text.rstrip() + "\n", encoding="utf-8")
print("Profile enhancements applied")

# Workflow trigger marker
