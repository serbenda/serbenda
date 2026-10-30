# Mantenimiento

## Cómo está montado

| Qué | Dónde |
|---|---|
| La web (`bendi.dev`, también `serbenda.github.io`) | repo [serbenda.github.io](https://github.com/serbenda/serbenda.github.io) |
| Lo que muestra la web de cada juego | `data/projects.json` del repo de la web, y las capturas en `img/games/` |
| Cada juego | su propio repo con su GitHub Pages, que sale solo en `bendi.dev/<nombre-del-repo>` |
| La recogida diaria de visitas, el README y sus tarjetas | este repo (`serbenda/serbenda`), workflow [Update profile](workflows/update-profile.yml) |
| Los datos de visitas | `data/traffic.json` de este repo; la web los lee de aquí |
| El dominio | Porkbun (DNS) y *Settings → Pages* del repo de la web |

`docs/` de este repo solo contiene una página que redirige a `bendi.dev`, para quien llegue por la dirección antigua.

## Añadir un juego nuevo

1. **Nombre del repo = dirección.** Si el repo se llama `mi-juego`, saldrá en `bendi.dev/mi-juego`. Minúsculas y guiones, sin espacios ni tildes.
2. **Activa GitHub Pages** en *Settings → Pages* del repo del juego.
3. **No pongas nada en "Custom domain"** del juego. Vacío hereda `bendi.dev`; si lo rellenas, se sale del dominio.
4. **Rutas relativas** en el HTML: `img/logo.png` o `./js/juego.js`, nunca `/img/logo.png`.
5. **Contador de visitas**, antes de `</body>`:
   ```html
   <script>window.goatcounter = { path: '/mi-juego/' };</script>
   <script data-goatcounter="https://serbenda.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
   ```
   Y donde empieza una partida:
   ```js
   try { globalThis.goatcounter?.count?.({ path: "partida/mi-juego", title: "Partida empezada", event: true }); } catch {}
   ```
6. **Que salga en la web y en el README:** añade su entrada en `data/projects.json` del repo de la web (título, textos en español e inglés, etiquetas y la captura en `img/games/mi-juego.webp`, de 640x360). El README se actualiza solo a la mañana siguiente, o al lanzar el workflow a mano.

No hay que tocar nunca el DNS, el token ni GoatCounter para añadir un juego.

## Renovar el token de visitas

Las vistas de cada repositorio las lee el workflow [Update profile](workflows/update-profile.yml) con un token guardado en el secret `TRAFFIC_TOKEN`. GitHub avisa por correo unos días antes de que caduque.

**Para renovarlo:**

1. Entra en [Personal access tokens](https://github.com/settings/personal-access-tokens), abre **visitas-perfil** y pulsa **Regenerate token**. Elige la caducidad y copia el token nuevo, que solo se ve una vez.
2. En [los secrets del repo](https://github.com/serbenda/serbenda/settings/secrets/actions), pulsa el lápiz de `TRAFFIC_TOKEN`, pega el token nuevo y guarda. No lo pegues en ningún otro sitio.
3. En [Actions → Update profile](https://github.com/serbenda/serbenda/actions/workflows/update-profile.yml), pulsa **Run workflow** y comprueba que termina en verde.

**Si hay que crearlo de cero:** token *fine-grained*, acceso a **All repositories** y un único permiso, **Administration: Read-only**. GitHub añade solo *Metadata: Read-only*. No uses un token *classic*.

**Si caduca sin renovar**, la web sigue funcionando y el histórico guardado no se pierde. Solo quedan sin recoger las vistas a los repos, porque GitHub guarda nada más que los últimos 14 días. Las visitas a los juegos no dependen del token: las cuenta GoatCounter.

## Dominio bendi.dev

- Registrado en Porkbun. Los registros DNS son 4 `A` (185.199.108-111.153), 4 `AAAA` (2606:50c0:8000-8003::153) y un `CNAME` `www` → `serbenda.github.io`. No hay que cambiarlos.
- El dominio se pone **solo** en *Settings → Pages* del repo `serbenda.github.io`, con *Enforce HTTPS* marcado.
- Renovación anual en Porkbun.

## GoatCounter

Las visitas y partidas de los juegos las cuenta [serbenda.goatcounter.com](https://serbenda.goatcounter.com). Para que la web las muestre, en *Settings* tiene que estar marcada **Allow adding visitor counts on your website**. Si el código de la cuenta cambia, guárdalo como variable `GOATCOUNTER_CODE` de este repo y cámbialo también en el `index.html` de la web y en el de cada juego.

## Imágenes generadas

`og.png` (la imagen al compartir la web) y `assets/header.png` (la cabecera de este README) salen de las plantillas `og.html` y `header.html` del repo de la web: se abren en un navegador a 1200x630 y 1280x320 y se hace una captura.
