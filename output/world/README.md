# Vila da Folha and mining revision

Implemented directly in Anime Mining Simulator, place 101959830085647. Studio backup: ServerStorage.BeforeFolhaMining_1788919666.

## Environment

FolhaEnvironment.lua builds Area1's sand quarry, terraced Plastic/Studs cliffs, original tree clones, river, waterfall, two bridges, timber lodge, mine tunnel, cart and rails, lanterns, vines, Leaf banners and carved stone relief. The central boss and 30 curated ore placements keep navigation routes clear. Ore variants retain their existing rewards and gain blue, gold and purple visual accents. Other areas keep their existing environment generator.

The old lobby cliffs intersecting the area's entrance were backed up and trimmed to the boundary. The baseplate was split around this area's footprint so the recessed river remains visible and navigable while surrounding floor levels are preserved. The existing Chakra gacha was repositioned to ground level near the entrance, with its distant label reduced. Area arrivals now face into the quarry.

AmbienteFolha.client.lua animates water currents, waterfall textures and lanterns, with distance limits and the existing VFX preference respected.

## Mining

See ../mining for the source copies. MiningSwing.lua now contains an authored 0.72-second strike with anticipation, torso rotation, descending tool motion, contact at 0.34 seconds and recovery. The tool rotates around its grip to aim toward the rock. Big Axe locomotion remains in place and resumes after the swing.

MiningGeometry.lua is shared by client and server: approach offset 2.05 studs, maximum contact distance 3.05 studs, nearest point on the ore's solid bounds, and a line-of-sight check. Collision boxes exclude scattered rubble. The server schedules damage at impact, rechecking range, tool, player, rock and capacity. The previous 11/26-stud bonus reach was removed. Local impact dust, sparks and a short tool trail support the animation.

The PicaretaTool delivery now avoids duplicate equipment and ignores a stale deferred equip request after its tool has been replaced.

## Validation

- Real R15/AnimationConstraint avatar: pickaxe head measured 0.197 studs from the requested contact point at impact; the character returned to Big Axe idle afterward.
- Real mouse click on a rock: character approached to a 1.93-stud contact gap and performed a validated strike.
- Client-to-server remote: distant hit rejected; no immediate or early damage; damage observed at impact; moving away before impact cancelled damage. Temporary high-HP rocks avoided break rewards during validation.
- Navigation paths succeeded from the entrance to the lodge, mine, shrine, bridge and boss approach.
- Water current movement was observed in Play.
- Final equip test: current pickaxe equipped, Big Axe ready, no runtime errors in the console.

The generated edit-mode area was refreshed after testing. Play mode was stopped. No publishing was performed.
