# OffBabel, demo runsheet

**One line:** An offline AI language tutor on a Reachy Mini robot. Talk to it to practice a
language, or practice sign to the camera. Everything runs on-device, no internet.

**Two modes (keep it simple):**
- **Speak**, talk with Reachy, it replies and corrects you. For anyone learning a language.
- **Sign**, practice fingerspelling to the webcam, Reachy reacts. For practicing sign / people who do not speak.

**Why a robot (in one breath):** it is a tutor you just talk to, hands-free, more engaging than a
screen, and it runs fully offline. You can even turn the screen off and keep learning.

## Before you go on (Mac = demo machine)
- Exo running with the model loaded; `python -m offbabel.server` running; UI built (`npm run build`).
- Reachy connected (`OFFBABEL_ROBOT=1`); speakers next to Reachy; Chrome fullscreen at `localhost:8500`.
- **Sign model trained ON THE MAC** under stage lighting (`capture A,B,G,W` then `train`).
- No-internet LAN locked; venue wifi forgotten (or airplane mode ready).
- Sanity: `python -m offbabel.doctor`, then one full dry run with wifi off.

## The run (~2 minutes)
1. **Hook (10s):** "OffBabel, an AI language tutor that runs entirely on this robot. No internet, no cloud, all on-device."
2. **Speak, English (30s):** tap Speak. Reachy greets and asks a question. Answer it, then make one mistake on purpose, Reachy corrects it gently. Captions + translation on screen.
3. **The robot moment (15s):** "And I do not even need the screen." Turn the screen away / lid down and keep talking, Reachy keeps tutoring by voice. "A tutor you just talk to."
4. **Speak, Spanish (20s):** flip the language pill to ES. Quick exchange; the English translation caption lets everyone follow. "Same tutor, another language, still offline."
5. **Sign (25s):** tap Sign. It shows a letter; form A, B, G, W; it recognizes each on-device through the webcam and Reachy celebrates. "It practices sign too, all vision on-device."
6. **Memory (10s):** open Progress. "It remembers what you struggled with, locally, and knows what to review."
7. **Offline reveal (10s):** show airplane mode / pull the router WAN. "Everything you just saw ran with no internet."

## Sponsor name-drops (work in naturally)
- **Exo:** the language model runs locally via Exo.
- **Cognee:** the memory of what you struggled with is a local knowledge graph via Cognee.
- **Captur:** the sign recognition is on-device visual validation, in Captur's spirit.
- **Cosine:** we built a lot of this with Cosine.

## Fallbacks (don't announce, just know them)
- Exo flaky -> the scripted conversation runs the exact same flow.
- Sign shaky -> you trained A, B, G, W; sign those, or skip to Progress.
- Robot drops -> the on-screen avatar carries the emotion; the demo continues.

## Close
"OffBabel: an offline robot tutor. Talk to it, or sign to it. Two ways to learn, no internet, all on-device."
