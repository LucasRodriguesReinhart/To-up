# Final audio fixes: local integration handoff

Historical handoff snapshot. These patches were subsequently installed by the root task. The final deliverable sources are in `../src/`; ExpeditionClient also includes later UI touch/layout corrections. Do not replace the final Client with the older patch result listed here. `../VERIFICACAO_FINAL.json` records the final installed check.

All changes are additive delivery metadata or local audio preference behavior. No gameplay awards, prices, quantities, RNG distributions, inventory rules, daily advancement, or datastore names were changed.

## Installation set

Install these six sources together in Edit mode after backing up the current Studio sources. Start a fresh Play session afterward so cached ModuleScripts reload. No Studio operation was performed by this subtask.

- `ServerScriptService/Core/PlayerData.lua` — `ModuleScript`; result `output\audio-v3\final-fixes\src\ServerScriptService\Core\PlayerData.lua`.
  - Exact input SHA256: `e10ad661be4560811e88b1a11be5c7337659638fa927369770340dc7a0800283`.
  - Result SHA256: `6da2c8e5f12b320a862a7f3ead088def84de2acb91642a75268fff3cd2a7dcc7`.
  - Minimal patch: `output\audio-v3\final-fixes\patches\PlayerData.lua.patch`.
- `ServerScriptService/Core/Recompensas.lua` — `ModuleScript`; result `output\audio-v3\final-fixes\src\ServerScriptService\Core\Recompensas.lua`.
  - Exact input SHA256: `248a62a52cb220ae2d4d1771d9ad456504a10f1a7221a5950b2be8e1b15809d0`.
  - Result SHA256: `2af4d5711b6ce91ee5564df0f97b41027b9198400b50cf4ff29a61bf402ae69a`.
  - Minimal patch: `output\audio-v3\final-fixes\patches\Recompensas.lua.patch`.
- `ServerScriptService/Core/Retencao.lua` — `ModuleScript`; result `output\audio-v3\final-fixes\src\ServerScriptService\Core\Retencao.lua`.
  - Exact input SHA256: `e78db7086c1d70f34c0acf8bd79cf216fcf6a32a2a5bab38406cea0e11395a7f`.
  - Result SHA256: `048c613e7372205bf5be60f52591f61fc77ff896b36a22af935c034016ed7324`.
  - Minimal patch: `output\audio-v3\final-fixes\patches\Retencao.lua.patch`.
- `ServerScriptService/Core/Codigos.lua` — `ModuleScript`; result `output\audio-v3\final-fixes\src\ServerScriptService\Core\Codigos.lua`.
  - Exact input SHA256: `83240ed2a90f9ccecf2929e166a5c4f947aa676a6efa3ee2b8cd513076d10466`.
  - Result SHA256: `c2f0209177c5d41ff19851f85db46761f41148c362bceb9c6156cde75b70c1f3`.
  - Minimal patch: `output\audio-v3\final-fixes\patches\Codigos.lua.patch`.
- `StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua` — `LocalScript`; result `output\audio-v3\final-fixes\src\StarterPlayer\StarterPlayerScripts\ExpeditionClient.lua`.
  - Exact input SHA256: `0230b97fee18c88e5371d65f09e9222257e2e3656781f70f3da1a41360ea77dd`.
  - Result SHA256: `54bb1eda55024a6d869920c12ba87031262f5a5c4c9820593f79aad56ef46b5c`.
  - Minimal patch: `output\audio-v3\final-fixes\patches\ExpeditionClient.lua.patch`.
- `StarterPlayer/StarterPlayerScripts/MineracaoVisual.lua` — `LocalScript`; result `output\audio-v3\final-fixes\src\StarterPlayer\StarterPlayerScripts\MineracaoVisual.lua`.
  - Exact input SHA256: `2fbe9f4991470cd46b6781ef93a76f30bfdd24ff5b8f73789cb0b670f528671b`.
  - Result SHA256: `c91164f42a9222f3c1d5f9adce4310df80abcc717b440035ecd3b5b3bcb5c617`.
  - Minimal patch: `output\audio-v3\final-fixes\patches\MineracaoVisual.lua.patch`.

PlayerData, Recompensas, Retencao and Codigos are already written under `output/audio-v3/src/ServerScriptService/Core`. The two LocalScripts exist only under `final-fixes/src`: their active sources were deliberately left untouched. All originals used for this patch are captured under `final-fixes/bases`.

## Concurrent UI guard

ExpeditionClient must be merged into the latest UI source using the supplied patch. Require the manifest base SHA256 before copying the full generated result. If the hash differs, use the minimal patch against the newer source, review its three audio-only hunks, and recompile. Never replace newer UI work with a stale complete file.

Read-only applicability check from workspace:
```powershell
git apply --check --directory=output/ui-v2/src output/audio-v3/final-fixes/patches/ExpeditionClient.lua.patch
```

## Behavior

- Server preference updates no longer replicate old attribute values over newer local edits. Defaults/preferences still apply server-side on profile load; response and local preview own changes during the session.
- Daily/code return `audioReward` describing actual delivered rarity, coins and boost. Rare fallback and full inventory are respected.
- Daily/code snapshots carry transient `audioContext` only on the snapshot; metadata never enters the persisted profile.
- Hats retain their visual feedback with `audioContext` added. MineracaoVisual defers their daily/code sound to the one response cue. Ordinary mined hats are unchanged.
- The response selects one priority: delivered rarity, boost, then coins. Boost purchase snapshots retain their previous sound path.
- Collection completion keeps its visual banner but has no extra achievement sting for the same daily/code snapshot.

## Verification

`LOCAL_FIXTURE_QA.json`: six real sources compiled using official Luau CLI 0.738; 13 original-versus-revised transaction fixtures compare exact gameplay state, RNG selections, telemetry, feedback payloads and save-request counts after removing additive audio metadata. Includes daily 2/5/7, multi-hat, rarity fallback, full inventory, all current codes, invalid and duplicate code. Captured profile states have SHA256 hashes.

Four additional checks pass: normal purchase boost/mined hat retained; stale preference patch does not write client attributes and whitelist holds; snapshot context is transient and clears on ordinary synchronization; transaction achievement sound false preserves the banner.

Only mocks and local memory were used. There were no real transactions, datastore writes, Studio calls or player-profile changes. Fixtures use immediate task scheduling; network/real persistence and auditory approval remain separate validation.
