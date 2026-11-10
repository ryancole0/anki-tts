# anki-tts

Minimal Google Cloud Text-to-Speech (TTS) CLI. Sends text, receives MP3 audio.

# 1. Google Cloud Setup

### A. Create a Project

1. Go to: https://console.cloud.google.com/
2. Create a new project (or select an existing one).

---

### B. Enable Required Service

You must enable:

- **Cloud Text-to-Speech API**

In Console:

1. Go to **APIs & Services → Library**
2. Search for **Text-to-Speech**
3. Click **Cloud Text-to-Speech API**
4. Click **Enable**
5. Repeat for **Identity and Access Management (IAM) API**
6. Do not enable other services unless you are sure you know what you are doing :)

Direct link (project-specific):
* https://console.cloud.google.com/apis/library/texttospeech.googleapis.com
---

### C. Create a Service Account
1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Name it (e.g., `anki-tts-sa`)
4. Do not assign a role
5. Click **Create and Continue**

---

### D. Create a Budget with Alerts
Even though Cloud Text-to-Speech usage is inexpensive at small scale, it is good practice to enforce budget limits.

1. Go to **Billing → Budgets & alerts**
2. Click **Create budget**
3. Select your billing account
4. Scope it to:
   - Entire project, or
   - Just the project used for `anki-tts`
5. Set a monthly budget amount (e.g. `$5` or `$10`)
6. Configure alert thresholds:
   - 50%
   - 90%
   - 100%
7. Click "Finish"

Alerts are sent via email (and optionally Pub/Sub).

This ensures you are notified before costs escalate.

---

### E. Create JSON Key
**NOTE** that following these instructions creates the potential for abuse if your key credential (json) is exposed.  There are steps taken here to prevent your key from being stored in Git by excluding the .secrets folder, but be aware that sharing your key gives access to your GCP platform and by extension your billing account.
1. Click your new service account
2. Go to **Keys** tab
3. Click **Add Key → Create new key**
4. Select **JSON**
5. Download the file (happens automatically)
6. rename to gcp-tts-key.json and copy to /src/.secrets/ folder 

# Local Setup

1) Install Hatch (if needed):
```bash
pipx install hatch
```
2) Run a synthesis:
```bash
hatch run anki-tts "Hei, hvordan går det?" -o out.mp3
```

### Options

* Language code (default nb-NO):
```bash
hatch run anki-tts "God morgen" --lang nb-NO -o god_morgen.mp3
```
* Pin a specific voice:
  * Note that Google doesn't offer a voice with Bergen dialect.  Notevibes does, but requires a paid account (500 NOK+)
```bash
hatch run anki-tts "Takk" --voice nb-NO-Wavenet-G -o takk.mp3
```
* Generate a set of files from a CSV, with manifest to be used downstream:
  * note that the `lang-map` argument maps the Column names in the column header to codes used for langauge translation
``` bash
hatch run anki-tts csv \
  --in-csv ./example/example.csv \
  --media-dir anki_media \
  --out-manifest ./example/example_manifest.yaml \
  --lang-map "English=en-US,Bokmål=nb-NO" \
  --skip-deck
```
* Generate audio files and manifest, and create an anki deck to be imported into Anki Droid (or similar)
``` bash
hatch run anki-tts csv \
  --in-csv ./example/example.csv \
  --media-dir anki_media \
  --out-manifest ./example/example_manifest.yaml \
  --lang-map "English=en-US,Bokmål=nb-NO" \
  --deck-name ./example/example_deck.apkg
```
``` bash
in_name="vocab"
out_name="new_vocab"
hatch run anki-tts csv \
  --in-csv $in_name.csv \
  --media-dir anki_media \
  --out-manifest $out_name.yaml \
  --lang-map "English=en-US,Bokmål=nb-NO" \
  --deck-name $out_name.apkg
```