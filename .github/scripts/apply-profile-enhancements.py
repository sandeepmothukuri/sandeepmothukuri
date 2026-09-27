#!/usr/bin/env python3
from pathlib import Path

README = Path("README.md")
text = README.read_text(encoding="utf-8")

# Keep the current automated status block, but remove the stale UK timestamp.
text = text.replace(
    'https://img.shields.io/badge/Status-%F0%9F%9B%8C%20Weekend%20%C2%B7%20UK%2022:24%20BST-8b949e?style=flat-square&labelColor=132f4c',
    'https://img.shields.io/badge/Status-%F0%9F%9B%8C%20Weekend%20%C2%B7%20India%20IST-8b949e?style=flat-square&labelColor=132f4c',
)
text = text.replace(
    'alt="Status: 🛌 Weekend · UK 22:24 BST"',
    'alt="Status: 🛌 Weekend · India IST"',
)

# Automated portfolio sections. Markers make this idempotent and safe for future runs.
top_repos = '''
## 🏆 Top Repositories — Last 30 Days

> Automatically ranked daily using repository traffic: **views + clones**, with stars and forks shown for additional context.

<!-- TOP-REPOS START -->

| Rank | Repository | Views | Clones | Stars | Forks |
|---|---|---:|---:|---:|---:|
| 🥇 | **Enterprise-Detection-Engineering-SOC-Lab** | — | — | — | — |
| 🥈 | **AI-Augmented-SOC-Lab** | — | — | — | — |
| 🥉 | **PromptShield** | — | — | — | — |

<!-- TOP-REPOS END -->

> 🔄 This section is automatically recalculated from the latest repository traffic history.
'''

focus = '''
## 🎯 Security Engineering Focus

| Domain | Focus |
|---|---|
| 🔎 **Detection Engineering** | Sigma · KQL · SPL · MITRE ATT&CK · Detection-as-Code |
| 🛡️ **SOC Operations** | L2/L3 triage · Incident Response · Threat Hunting · RCA |
| 🤖 **AI Security** | LLM Security · Prompt Injection · AI-assisted SOC · AI Firewall |
| ⚙️ **Security Automation** | Python · PowerShell · SOAR · CI/CD · Automated Enrichment |
| ☁️ **Cloud Security** | Microsoft Defender · Sentinel · Azure · AWS |
| 🧪 **Adversary Simulation** | MITRE ATT&CK · Caldera · Atomic Red Team |
'''

projects = '''
## 🧩 Projects → Capabilities

| Project | Demonstrates |
|---|---|
| 🔥 [SOCForge](https://github.com/sandeepmothukuri/socforge) | SOC triage · investigation · detection engineering · AI-assisted security operations |
| 🤖 [AI-SOC-Decision-Engine](https://github.com/sandeepmothukuri/AI-SOC-Decision-Engine) | AI-assisted SOC decisioning · evidence analysis · risk assessment |
| 🛡️ [PromptShield](https://github.com/sandeepmothukuri/PromptShield) | Prompt injection defense · LLM security · AI application protection |
| 🛡️ [PromptSentinel](https://github.com/sandeepmothukuri/PromptSentinel) | AI firewall · prompt injection detection · SARIF/SIEM integration |
| 🧠 [AI-Augmented-SOC-Lab](https://github.com/sandeepmothukuri/AI-Augmented-SOC-Lab) | AI SOC experimentation · detection engineering · threat hunting |
| 🎯 [sentinel-detection-engine](https://github.com/sandeepmothukuri/sentinel-detection-engine) | KQL · Microsoft Sentinel · MITRE ATT&CK · detection-as-code |
'''

principles = '''
## 🏗️ Engineering Principles

`Detection-as-Code` · `Evidence-Driven Investigation` · `Automation-First SOC` · `MITRE ATT&CK Mapping` · `Reproducible Security Labs` · `AI-Assisted Analysis` · `CI/CD Validation` · `Measurable MTTD / MTTR Reduction`
'''

analytics = '''
## 📊 Automated GitHub Analytics

Your profile automatically tracks:

- 👁 Repository views
- 📥 Repository clones
- 👥 Unique visitors
- 👤 Unique cloners
- ⭐ Stars
- 🍴 Forks
- 📦 Release downloads
- 📈 30-day traffic
- 🏆 Top repository ranking
- 🧪 Public repository discovery

New public repositories are automatically discovered by the daily metrics workflow.
'''

# Remove previously generated sections before reinserting them, preventing duplicates.
section_markers = [
    ("## 🏆 Top Repositories — Last 30 Days", "## 🎯 Security Engineering Focus"),
    ("## 🎯 Security Engineering Focus", "## 🧩 Projects → Capabilities"),
    ("## 🧩 Projects → Capabilities", "## 🏗️ Engineering Principles"),
    ("## 🏗️ Engineering Principles", "## 📊 Automated GitHub Analytics"),
]
for start, end in section_markers:
    if start in text:
        a = text.index(start)
        b = text.index(end, a) if end in text[a + len(start):] else None
        if b is not None:
            text = text[:a].rstrip() + "\n\n" + text[b:].lstrip()

# If analytics is the last generated section, remove it through the next heading.
if "## 📊 Automated GitHub Analytics" in text:
    a = text.index("## 📊 Automated GitHub Analytics")
    rest = text[a + len("## 📊 Automated GitHub Analytics"):]
    next_heading = rest.find("\n## ")
    b = a + len("## 📊 Automated GitHub Analytics") + (next_heading if next_heading >= 0 else len(rest))
    text = text[:a].rstrip() + "\n\n" + text[b:].lstrip()

# Insert portfolio sections after Currently focused, before Ask me about.
anchor = "## 💬 Ask me about"
if anchor in text:
    block = top_repos + focus + projects + principles + analytics + "\n"
    text = text.replace(anchor, block + anchor, 1)

README.write_text(text.rstrip() + "\n", encoding="utf-8")
print("Profile enhancements applied")
