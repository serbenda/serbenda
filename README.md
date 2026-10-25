<div align="center">

<img src="assets/header.svg" alt="Santiago · Automation Platform Engineer" width="100%">

**I turn manual operations into reviewed, reliable automation, and I'm the last check before it hits production.**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sergio-santiago-benda%C3%B1a-quesada/)
[![X](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/serbenda)
[![Farcaster](https://img.shields.io/badge/Farcaster-855DCD?style=for-the-badge&logo=farcaster&logoColor=white)](https://warpcast.com/serbenda)

**🇬🇧 English** · [🇪🇸 Español](README.es.md)

</div>

---

## 🧭 About me

I'm **Sergio Santiago Bendaña Quesada**, an engineer with **15+ years** across infrastructure automation, systems engineering and software development.

My day-to-day sits right between *"it works on my machine"* and *"it runs every night in production"*:

- ⚙️ **Rundeck automation**: I review the jobs technical teams deliver (Shell Script and Python plugins) together with the code behind them in GitHub.
- 🛡️ **Release gatekeeping**: nothing reaches production until it is correct, safe, idempotent and easy to roll back.
- 🗂️ **GitHub as the source of truth**: every request is tracked in GitHub Projects from delivery to production, and the boring parts run on GitHub Actions.

Before that I built infrastructure as code with Terraform and Ansible, migrated VMware estates to OpenStack, ran Big Data platforms on Cloudera and shipped full-stack apps with Node.js and React. I also hold a **Master's in Blockchain**.

---

## 🔁 How I ship automation

```mermaid
flowchart LR
    A[👥 Team delivers job<br/>+ code in GitHub] --> B{🔍 Review}
    B -->|changes requested| A
    B -->|approved| D[🗂️ GitHub Projects<br/>status: ready]
    D --> E[🚀 Promote to<br/>production]
    E --> F[📈 Monitor<br/>& feedback]
    F -.-> A

    classDef step fill:#0f1426,stroke:#38bdf8,color:#e2e8f0
    classDef gate fill:#1a1033,stroke:#a78bfa,color:#f8fafc
    classDef prod fill:#062a1e,stroke:#36d399,color:#f8fafc
    class A,D,F step
    class B gate
    class E prod
```

<details>
<summary><b>📋 What I check before anything goes to production</b></summary>
<br>

| Area | What I look for |
|---|---|
| **Correctness** | Does the job do exactly what the request says, with sensible defaults and validated options? |
| **Safety** | No secrets in plain text, least privilege, no destructive command without a guard. |
| **Idempotency** | Running it twice must not break anything. |
| **Failure handling** | Timeouts, retries, clear exit codes and an error message a human can act on. |
| **Rollback** | If it goes wrong at 3 a.m., how do we undo it? |
| **Code quality** | Readable Shell and Python, `set -euo pipefail`, linting, no copy-paste drift between environments. |
| **Traceability** | Linked to its card in GitHub Projects, versioned, and reviewable later. |

</details>

---

## 🛠️ Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=bash,py,js,nodejs,react,html,css,solidity&perline=8" alt="Languages"><br><br>
  <img src="https://skillicons.dev/icons?i=ansible,terraform,jenkins,githubactions,docker,kubernetes,linux,git&perline=8" alt="Automation and platforms"><br><br>
  <img src="https://skillicons.dev/icons?i=aws,azure,github,vscode&perline=8" alt="Cloud and tools">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Rundeck-F73F39?style=flat-square" alt="Rundeck">
  <img src="https://img.shields.io/badge/OpenStack-ED1944?style=flat-square&logo=openstack&logoColor=white" alt="OpenStack">
  <img src="https://img.shields.io/badge/Packer-02A8EF?style=flat-square&logo=packer&logoColor=white" alt="Packer">
  <img src="https://img.shields.io/badge/Cloudera-F96702?style=flat-square&logo=cloudera&logoColor=white" alt="Cloudera">
  <img src="https://img.shields.io/badge/GitHub_Projects-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub Projects">
</p>

---

## 🚀 Featured projects

<table>
<tr>
<td width="33%" valign="top">

### 🏃 [School Rush](https://github.com/serbenda/school-rush)
A cartoon race to get the kids to school before the 9:00 bell. Built to play with my daughters.

`HTML5 Canvas` `Vanilla JS` `0 deps` `GitHub Pages`

**[▶ Play it](https://serbenda.github.io/school-rush/)**

</td>
<td width="33%" valign="top">

### 🛡️ [FrameBlock](https://github.com/serbenda/frameblock)
Framework for building secure, scalable Web3 applications. Final project of my Master's in Blockchain.

`JavaScript` `Blockchain` `Web3`

</td>
<td width="33%" valign="top">

### 🏦 [Bankinter VISA → CSV](https://github.com/serbenda/bankinter-visa-pdf-to-csv)
Extracts transactions from Bankinter VISA PDF statements into clean CSV, ready for Excel or Power BI.

`Python` `PDF parsing` `CLI`

</td>
</tr>
</table>

---

## ⚡ Latest activity

<table>
<tr>
<td width="55%" valign="top">

<!-- ACTIVITY:START -->
- **[hemiciclo-fighters](https://github.com/serbenda/hemiciclo-fighters)** · `HTML` — Juego de lucha 2D estilo recreativa de los 90 con políticos ficticios. HTML + JS, sin dependencias. <sub>(updated today)</sub>
- **[school-rush](https://github.com/serbenda/school-rush)** · `HTML` — Despierta, desayuna, asea, viste y esquiva el tráfico: ¡lleva a los peques al cole antes de la campana! 🏫⏰ <sub>(updated today)</sub>
- **[chapas](https://github.com/serbenda/chapas)** · `JavaScript` · ⭐ 1 — Juego de chapas de los 80: la vuelta ciclista por turnos, para jugar en el móvil o la tablet. Hecho para jugar con mis hijas. <sub>(updated today)</sub>
- **[skills-introduction-to-github](https://github.com/serbenda/skills-introduction-to-github)** — My clone repository <sub>(updated 10 months ago)</sub>
- **[testgit](https://github.com/serbenda/testgit)** — No description yet. <sub>(updated 1 year ago)</sub>
<!-- ACTIVITY:END -->

<sub>🤖 Refreshed every day by a GitHub Action in this repo, because I automate everything.</sub>

</td>
<td width="45%" valign="top" align="center">

<img src="assets/stats.svg" alt="Public GitHub stats" width="100%">

</td>
</tr>
</table>

---

## 🏆 Highlights

- 🛡️ Act as the **review and promotion gate for Rundeck automation**, with GitHub Projects as the single source of truth from delivery to production.
- ⏱️ Automated infrastructure provisioning with **Terraform Enterprise**, cutting deployment times significantly.
- ☁️ Migrated **VMware workloads to OpenStack**, improving resource usage and reducing costs.
- 🔐 Designed secure **CI/CD pipelines** that made teams faster without cutting corners.
- 🧰 Built **Python** and **Shell** tooling that removed hours of repetitive manual work.
- 📊 Delivered **Big Data** platforms on Cloudera for real-time analytics.

---

<div align="center">

**Currently:** making automation reviews faster and more consistent · building small games with my kids · tinkering with a homelab

<sub>Open to talking about automation, platform engineering and safe releases. Find me on <a href="https://www.linkedin.com/in/sergio-santiago-benda%C3%B1a-quesada/">LinkedIn</a>.</sub>

</div>
