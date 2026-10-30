<div align="center">

<img src="assets/header.svg" alt="Bendi · Automation Platform Engineer" width="100%">

**Convierto operaciones manuales en automatización revisada y fiable, y soy el último control antes de producción.**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sergio-santiago-benda%C3%B1a-quesada/)
[![X](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/serbenda)
[![Farcaster](https://img.shields.io/badge/Farcaster-855DCD?style=for-the-badge&logo=farcaster&logoColor=white)](https://warpcast.com/serbenda)
[![Mi web](https://img.shields.io/badge/Mi_web-0f1426?style=for-the-badge&logo=githubpages&logoColor=38bdf8)](https://serbenda.github.io/serbenda/)

![Visitas al perfil](https://komarev.com/ghpvc/?username=serbenda&label=Visitas%20al%20perfil&color=38bdf8&style=flat-square)

[🇬🇧 English](README.md) · **🇪🇸 Español**

</div>

---

## 🧭 Sobre mí

Soy **Sergio Bendaña**, *Bendi* en el trabajo, ingeniero con **más de 15 años** en automatización de infraestructura, ingeniería de sistemas y desarrollo de software.

Mi día a día está justo entre *"en mi máquina funciona"* y *"se ejecuta cada noche en producción"*:

- ⚙️ **Automatización con Rundeck**: reviso los jobs que entregan los equipos técnicos (plugins ShellScript y Python) junto con su código en GitHub.
- 🛡️ **Control de pase a producción**: nada llega a producción hasta que es correcto, seguro, idempotente y fácil de revertir.
- 🗂️ **GitHub como fuente de verdad**: cada petición se sigue en GitHub Projects desde la entrega hasta producción, y lo repetitivo lo hacen las GitHub Actions.

Antes construí infraestructura como código con Terraform y Ansible, migré entornos VMware a OpenStack, llevé plataformas Big Data con Cloudera y desarrollé aplicaciones full-stack con Node.js y React. También tengo un **Máster en Blockchain**.

---

## 🔁 Cómo llevo la automatización a producción

```mermaid
flowchart LR
    A[👥 El equipo entrega<br/>job + código en GitHub] --> B{🔍 Revisión}
    B -->|cambios pedidos| A
    B -->|aprobado| D[🗂️ GitHub Projects<br/>estado: listo]
    D --> E[🚀 Promoción a<br/>producción]
    E --> F[📈 Seguimiento<br/>y feedback]
    F -.-> A

    classDef step fill:#0f1426,stroke:#38bdf8,color:#e2e8f0
    classDef gate fill:#1a1033,stroke:#a78bfa,color:#f8fafc
    classDef prod fill:#062a1e,stroke:#36d399,color:#f8fafc
    class A,D,F step
    class B gate
    class E prod
```

<details>
<summary><b>📋 Qué reviso antes de que algo pase a producción</b></summary>
<br>

| Área | Qué miro |
|---|---|
| **Corrección** | ¿Hace el job exactamente lo que pide la petición, con valores por defecto sensatos y opciones validadas? |
| **Seguridad** | Sin secretos en claro, mínimo privilegio, ningún comando destructivo sin protección. |
| **Idempotencia** | Ejecutarlo dos veces no debe romper nada. |
| **Gestión de fallos** | Timeouts, reintentos, códigos de salida claros y mensajes de error que una persona pueda entender. |
| **Marcha atrás** | Si falla a las 3 de la mañana, ¿cómo se deshace? |
| **Calidad de código** | Shell y Python legibles, `set -euo pipefail`, linting y sin divergencias por copiar y pegar entre entornos. |
| **Trazabilidad** | Enlazado a su tarjeta en GitHub Projects, versionado y revisable después. |

</details>

---

## 🛠️ Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=bash,py,js,nodejs,react,html,css,solidity&perline=8" alt="Lenguajes"><br><br>
  <img src="https://skillicons.dev/icons?i=ansible,terraform,jenkins,githubactions,docker,kubernetes,linux,git&perline=8" alt="Automatización y plataformas"><br><br>
  <img src="https://skillicons.dev/icons?i=aws,azure,github,vscode&perline=8" alt="Cloud y herramientas">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Rundeck-F73F39?style=flat-square" alt="Rundeck">
  <img src="https://img.shields.io/badge/OpenStack-ED1944?style=flat-square&logo=openstack&logoColor=white" alt="OpenStack">
  <img src="https://img.shields.io/badge/Packer-02A8EF?style=flat-square&logo=packer&logoColor=white" alt="Packer">
  <img src="https://img.shields.io/badge/Cloudera-F96702?style=flat-square&logo=cloudera&logoColor=white" alt="Cloudera">
  <img src="https://img.shields.io/badge/GitHub_Projects-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub Projects">
</p>

---

## 🚀 Proyectos destacados

<table>
<tr>
<td width="33%" valign="top">

### 🏃 [School Rush](https://github.com/serbenda/school-rush)
Una carrera de dibujos animados para llevar a los peques al cole antes de que suene la campana de las 9:00. Hecho para jugar con mis hijas.

`HTML5 Canvas` `Vanilla JS` `0 deps` `GitHub Pages`

**[▶ Jugar](https://serbenda.github.io/school-rush/)**

</td>
<td width="33%" valign="top">

### 🛡️ [FrameBlock](https://github.com/serbenda/frameblock)
Framework para crear aplicaciones Web3 seguras y escalables. Proyecto final de mi Máster en Blockchain.

`JavaScript` `Blockchain` `Web3`

</td>
<td width="33%" valign="top">

### 🏦 [Bankinter VISA → CSV](https://github.com/serbenda/bankinter-visa-pdf-to-csv)
Extrae los movimientos de los extractos PDF de la VISA de Bankinter a CSV limpio, listo para Excel o Power BI.

`Python` `PDF` `CLI`

</td>
</tr>
</table>

---

## ⚡ Actividad reciente

<table>
<tr>
<td width="55%" valign="top">

<!-- ACTIVITY:START -->
- **[dungeons-and-deployments](https://github.com/serbenda/dungeons-and-deployments)** · `JavaScript` · ⭐ 1 · [▶ demo](https://serbenda.github.io/dungeons-and-deployments/) — Beat 'em up de fantasía en pixel art: cuatro héroes del equipo de desarrollo, solos o en cooperativo, cruzan las catacumbas del CPD, las cuevas del Mainframe y la nube. Sin dependencias, funciona en el navegador y en el móvil. <sub>(actualizado hoy)</sub>
- **[deploy-quest](https://github.com/serbenda/deploy-quest)** · `HTML` — Aventura de 8 bits con vista cenital: un dev con su teclado y su Escudo de IaC recorre las Catacumbas de Sistemas, consigue la Terminal SSH y la primera página del Grimorio de la Definition of Done. HTML5 + canvas, sin dependencias. <sub>(actualizado hoy)</sub>
- **[story-reader](https://github.com/serbenda/story-reader)** · `JavaScript` — Cuentos interactivos para leer en voz alta, pensados para la dislexia: pistas al azar, 4 niveles y reconocimiento de voz. <sub>(actualizado hoy)</sub>
- **[hemiciclo-fighters](https://github.com/serbenda/hemiciclo-fighters)** · `HTML` — Juego de lucha 2D estilo recreativa de los 90 con políticos ficticios. HTML + JS, sin dependencias. <sub>(actualizado hoy)</sub>
- **[school-rush](https://github.com/serbenda/school-rush)** · `JavaScript` · ⭐ 1 — Despierta, desayuna, asea, viste y esquiva el tráfico: ¡lleva a los peques al cole antes de la campana! 🏫⏰ <sub>(actualizado hoy)</sub>
<!-- ACTIVITY:END -->

<sub>🤖 Se actualiza cada día con una GitHub Action de este repo, porque lo automatizo todo.</sub>

</td>
<td width="45%" valign="top" align="center">

<img src="assets/stats.svg" alt="Estadísticas públicas de GitHub" width="100%">

</td>
</tr>
</table>

---

## 📈 Visitas

<p align="center">
  <a href="https://serbenda.github.io/serbenda/#visitas"><img src="assets/traffic.es.svg" alt="Vistas de mis repositorios y visitas a mis juegos en GitHub Pages" width="500"></a>
</p>

<p align="center"><sub>Las vistas a los repos salen de la API de tráfico de GitHub y las visitas a Pages de GoatCounter. El dashboard completo, por proyecto y por día, está en <a href="https://serbenda.github.io/serbenda/#visitas">mi web</a>.</sub></p>

---

## 🏆 Logros

- 🛡️ Soy el **filtro de revisión y promoción de la automatización en Rundeck**, con GitHub Projects como única fuente de verdad desde la entrega hasta producción.
- ⏱️ Automaticé el aprovisionamiento de infraestructura con **Terraform Enterprise**, reduciendo mucho los tiempos de despliegue.
- ☁️ Migré **cargas de VMware a OpenStack**, mejorando el uso de recursos y reduciendo costes.
- 🔐 Diseñé **pipelines de CI/CD** seguros que hicieron más rápidos a los equipos sin saltarse controles.
- 🧰 Creé herramientas en **Python** y **Shell** que eliminaron horas de trabajo manual repetitivo.
- 📊 Puse en marcha plataformas **Big Data** con Cloudera para analítica en tiempo real.

---

<div align="center">

**Ahora mismo:** haciendo las revisiones de automatización más rápidas y consistentes · creando juegos con mis hijas · trasteando con mi homelab

<sub>Encantado de hablar de automatización, ingeniería de plataformas y despliegues seguros. Encuéntrame en <a href="https://www.linkedin.com/in/sergio-santiago-benda%C3%B1a-quesada/">LinkedIn</a>.</sub>

</div>
