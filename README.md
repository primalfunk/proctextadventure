# proctextadventure


This little project is about trying to take an important game genre from my childhood, text adventures, and applying the idea of procedural generation so that the game is different each time it's played.

The data file branches first at thematic genres, and this is the primary future expansion point once the conditions are met with existing genre data, such that a bewildering array of genres will be part of the game; the first four which stubbed out are fantasy, sci-fi, post-apocalyptic, and western. To be considered further are: mystery, horror, historical, pirate, steampunk, noir, magical, lovecraftian, espionage, military, zombie, mythology, fairy tale, time travel, gothic, space opera, absurdist/dadaist, underwater exploration, alien invasion, heist, samurai, ninja, prehistoric, Biblical, robot uprising, and we could really go on for quite a while, couldn't we?

In the immediate next big implementation I will try to add in the experience/level and turn-based combat system, which were working very nicely in a previous version that I catastrophically destroyed and need to be rebuilt. 

The game loop will eventually be something like this (as currently imagined): traverse the map to find the key item, fighting enemies and gaining levels, finding stat-boosting armor and weapons, adding allies to your party, and then, when each "small" 9x9 map has been resolved, throwing the player into a new, similarly designed map starting all the way from a random genre, increase the level of the newly created enemies, and then just play with the math until the combat/leveling is fun and see what else it needs.


7.1.23 *** The data file is filled with all the supporting information. The very large task of filling in room data starts tomorrow. Hoping to get it finished to my satisfaction and on to leveling/combat before the end of the long weekend.