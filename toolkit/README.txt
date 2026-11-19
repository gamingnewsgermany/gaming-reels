TOOLKIT – Gaming Facts und News (Reels)
=======================================
bilder/   Wiederverwendbare KI-Bildbibliothek (16:9, je Reel anders zuschneiden/zoomen/einfärben)
sfx/      ElevenLabs-Soundeffekte (whoosh, kaching, scratch, coins, trombone, ding, stamp) – KEIN Airhorn
musik/    Hintergrundmusik (ruhig, spannend)
vorlagen/ Beispiel-Renderer (Kassenbon, Split-VS, Formular, Zeitreise, Meme-Post, Terminal, Speedtest)
elmix.py  mix(voice, musik, offset_s, dauer_s, [(zeit,"sfx",gain),...], out_wav) – Musik ~9 % unter Stimme, SFX ~22 %

Regeln: max. 1 neues KI-Bild pro Reel (Standard: 0), Skript 25–30 s, Stimmen rotieren (eleven_v4),
Ende immer "Folge dem Kanal für mehr Infos!", keine Tröte, Fakten mit Quellen prüfen.

COVER/THUMBNAIL (seit 17.11.2026 Pflicht):
- Video NICHT aus Schwarz einblenden – schon Frame 0 muss das volle Hook-Bild zeigen (Instagram nimmt sonst ein schwarzes Profil-Thumbnail).
- Zusätzlich <Dateiname ohne .mp4>_Cover.jpg (1080x1920, Hook-Frame mit vollständig eingeblendetem Text) nach videos/ committen
  und beim Posten als cover_url (jsDelivr-Link mit Commit-Hash) an create_video_post übergeben.

KI-KENNZEICHNUNG (seit 17.11.2026 Pflicht, Maltes Wunsch):
- Im ganzen Video und auf dem Cover dezent "KI-generiert" einblenden (kleines Badge, 30–36 px, nicht unter Instagram-Bedienelementen).
- In der Caption eigene Zeile: "🤖 Mit KI erstellt (Stimme & Bilder)".

EINHEITLICHES COVER: toolkit/vorlagen/cover.py <bild> "ZEILE 1" "ZEILE 2" <out.jpg> [akzent_hex]
- Immer dieses Layout (weiße Zeile + Akzentzeile, Inter Black, links, Mitte des Bildes, "GAMING FACTS & NEWS" + "KI-generiert").
- Max. 2 Zeilen à ca. 14 Zeichen. Akzentfarbe darf je Reel wechseln, Layout nie.

HOOK-REGEL: Die ersten 2 Sekunden brauchen Reibung – steile These, schockierende Zahl oder Ja/Nein-Frage
(Vorbild: 30-FPS-Reel, 78k Aufrufe, 33 % Skip). Reine Info-Hooks ("X ist erschienen") vermeiden.

JSDELIVR-LIMIT (seit 19.11.2026): Das Repo ist > 50 MB, jsDelivr liefert MP4s von main daher mit 403
("Package size exceeded"). Lösung: Video + Cover zusätzlich in einen eigenen Orphan-Branch post-<Nr> pushen
(nur diese 2 Dateien), dessen Commit-Hash für video_url/cover_url nutzen. Vorher mit
curl -s -o /dev/null -w "%{http_code}" <url> prüfen (curl -I zeigt hinter dem Proxy immer 200).
