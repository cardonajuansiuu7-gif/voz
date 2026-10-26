# Clonador de voz (Fish Audio)

Subes un audio de una voz, la guarda y luego conviertes cualquier texto a audio con esa voz.
Lo único que necesitas es tu API key de Fish Audio (gratis): https://fish.audio/app/api-keys

## En tu computadora

- Windows: doble clic en `iniciar.bat`
- Mac/Linux: doble clic (o ejecutar) `iniciar.command`

Se abre solo en http://localhost:5000. Pega tu API key arriba y listo.
(Necesitas tener Python instalado.)

## En internet (Railway)

1. Sube esta carpeta a un repositorio de GitHub.
2. En Railway: New Project > Deploy from GitHub repo > elige el repositorio.
3. En Settings > Networking pulsa Generate Domain.
4. Abre el enlace y pega tu API key en la página.

No definas ninguna variable en Railway: la clave la pone cada persona en su navegador,
así nadie puede gastar tus créditos aunque tengan el enlace.

## Notas

- Usa el modelo gratis `s2.1-pro-free` (se puede cambiar con la variable FISH_MODEL).
- Las voces se crean como privadas en tu cuenta de Fish Audio y se recuerdan en tu navegador.
- Clona solo voces propias o con permiso de la persona.
