# Wireframe betöltő

!! Ha a kód futtatásakor problémába akadnál akkor keress nyugodtan. !!

### Tartalom:
- Előfeltételek
- Müködés

## Előfeltételek
- Legyen a gépeden egy kódszerkesztő program, pl.: Visual Studio Code.
- Legyen a gépeden egy python interpreter, legegyszerűbben a Microsoft Store-ból tölthető le. 
- Legyen a gépeden letöltve a pip.
- Nyisd meg a projektet a kódszerkesztőben, majd a terminálba a következő command-ot futtasd: **pip install selenium**
- Futasd a kódot

## Mükődés
A kód mükődéséhez a következő adatok szükségesek:
- Az APEX workspace URL cime
- Az APEX workspace neve
- A felhasználó neved a workspace-hez
- A jelszavad a workspace-hez
- A wireframe zippeket tartalmazó mappa elérési útvonala 

A kód első futtatásakor a kód kérni fogja a fent említett adatokat. FONTOS! próbáld meg jól megadni az adatokat.
<br>
**Ha rossz adatokat adtál meg akkor két opciód van:**
- Törlöd a config.json fájlt. Ebben az esetben újra el kell inditani a kódot.
- Átirod az adatokat a config.json fájlban