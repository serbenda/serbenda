# Mantenimiento

## Renovar el token de visitas

Las vistas de cada repositorio las lee el workflow [Update profile](workflows/update-profile.yml) con un token guardado en el secret `TRAFFIC_TOKEN`. GitHub avisa por correo unos días antes de que caduque.

**Para renovarlo:**

1. Entra en [Personal access tokens](https://github.com/settings/personal-access-tokens), abre **visitas-perfil** y pulsa **Regenerate token**. Elige la caducidad y copia el token nuevo, que solo se ve una vez.
2. En [los secrets del repo](https://github.com/serbenda/serbenda/settings/secrets/actions), pulsa el lápiz de `TRAFFIC_TOKEN`, pega el token nuevo y guarda. No lo pegues en ningún otro sitio.
3. En [Actions → Update profile](https://github.com/serbenda/serbenda/actions/workflows/update-profile.yml), pulsa **Run workflow** y comprueba que termina en verde.

**Si hay que crearlo de cero:** token *fine-grained*, acceso a **All repositories** y un único permiso, **Administration: Read-only**. GitHub añade solo *Metadata: Read-only*. No uses un token *classic*.

**Si caduca sin renovar**, la web sigue funcionando y el histórico guardado no se pierde. Solo quedan sin recoger las vistas a los repos, porque GitHub guarda nada más que los últimos 14 días. Las visitas a los juegos no dependen del token: las cuenta GoatCounter.

## GoatCounter

Las visitas y partidas de los juegos las cuenta [serbenda.goatcounter.com](https://serbenda.goatcounter.com). Para que la web las muestre, en *Settings* tiene que estar marcada **Allow adding visitor counts on your website**. Si el código de la cuenta cambia, guárdalo como variable `GOATCOUNTER_CODE` del repo y cámbialo también en `docs/index.html` y en el `index.html` de cada juego.
