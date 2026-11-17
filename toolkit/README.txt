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
