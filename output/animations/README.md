# Big Axe locomotion

Source: [Big Axe Stance Bundle](https://www.roblox.com/bundles/272148363726799/Big-Axe-Stance-Bundle), by Lotucupi.

The bundle ID is 272148363726799; it is not an Animation asset ID. The eight embedded KeyframeSequences were retrieved from the bundle's animation assets and stored in ReplicatedStorage.BigAxeKeyframes in Studio.

| Clip | Animation ID | Frames |
| --- | --- | --- |
| idle | 81487174764898 | 61 |
| walk | 118496842640947 | 31 |
| run | 108702410938489 | 26 |
| jump | 84582505592766 | 16 |
| fall | 91165762027983 | 16 |
| climb | 116523204352944 | 26 |
| swim | 128083845192579 | 26 |
| swimidle | 116148871336274 | 26 |

LocomocaoBigAxe.client.lua mirrors StarterPlayer.StarterPlayerScripts.LocomocaoBigAxe. It samples the embedded linear poses for R15 characters using Motor6D or AnimationConstraint, on each client for all player characters. It preserves the default Animate script for other actions, yields to MiningSwing and emotes, and blends back into locomotion. R6 keeps its existing animations.

The previous LocomocaoPadrao loader and its unavailable Animation reference were moved to ServerStorage.BeforeBigAxeLocomotion_1788918972. The mining swing source was unchanged.

Validation in Studio Play: observed idle, walk, run, jump, fall, mining, and return to idle using the player's AnimationConstraint rig. Idle joints changed over time; there were no runtime errors in the final test. Climb/swim sequences were imported and their state routing implemented, but were not tested on a live ladder or swimming area. Play mode was stopped afterward. No experience publishing was performed.
