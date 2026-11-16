# gaming-reels
Speicher für den Instagram-Kanal „Gaming Facts und News“.
- `toolkit/` – Bildbibliothek, ElevenLabs-Soundeffekte, Musik, Vorlagen, elmix.py
- `videos/` – fertige Reels (öffentlich, damit Instagram sie abholen kann)
- `shorts-log.txt` – Liste aller Reels (Nummer, Datum, Thema, Vorlage, Stimme, gepostet/Media-ID)

Instagram holt die Videos über jsDelivr ab (liefert video/mp4, raw.githubusercontent nicht):
`https://cdn.jsdelivr.net/gh/gamingnewsgermany/gaming-reels@<commit>/videos/<datei>.mp4` (max. 20 MB pro Datei)
