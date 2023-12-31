# proctextadventure


This little project is about trying to take an important game genre from my childhood, text adventures, and applying the idea of procedural generation so that the game is different each time it's played.

The data file branches first at thematic genres, and this is the primary future expansion point once the conditions are met with existing genre data, such that a bewildering array of genres will be part of the game; the first four which stubbed out are fantasy, sci-fi, post-apocalyptic, and western. To be considered further are: mystery, horror, historical, pirate, steampunk, noir, magical, lovecraftian, espionage, military, zombie, mythology, fairy tale, time travel, gothic, space opera, absurdist/dadaist, underwater exploration, alien invasion, heist, samurai, ninja, prehistoric, Biblical, robot uprising, and we could really go on for quite a while, couldn't we?

In the immediate next big implementation I will try to add in the experience/level and turn-based combat system, which were working very nicely in a previous version that I catastrophically destroyed and need to be rebuilt. 

The game loop will eventually be something like this (as currently imagined): traverse the map to find the key item, fighting enemies and gaining levels, finding stat-boosting armor and weapons, adding allies to your party, and then, when each "small" 9x9 map has been resolved, throwing the player into a new, similarly designed map starting all the way from a random genre, increase the level of the newly created enemies, and then just play with the math until the combat/leveling is fun and see what else it needs.

7.2.23 *** One thing I've discovered to be very helpful is to maintain a list of the exact requirements under which useful data can be created for the game. Each distinct object in the structure needs a very careful definition to try and minimize "unrealism" as they'll all be combined together with other randomly selected objects.

For room "names":
1. The room names should logically fit within the general conception of a sub-area or visitable place within or in the immediate locality of the prompted location.
2. Room names should prioritize adhering to the genre and setting, without the inclusion of any adjectives or modifiers. Additional dimensions can be added later.
3. Keep the room names simple, utilizing words that are synonymous with or well-known and recognizable parts of the given prompt location or area type.
4. Adjectives should not be used in the room names, as they will not be included.
5. The room names should provide a broad variety of simple words that reflect different areas or sub-areas within the prompted location.
6. Format the output as a JSON-type array of comma-separated strings of room names.

For adjectives:
1. Ordinary Universal Adjectives: Include 10 general adjectives that could describe any room, not specific to the genre or room type. These should be common descriptors that capture basic features, such as size, brightness, temperature, etc.
2. Room Universality: The adjectives should not only be applicable to the given room type, but also be fitting for potential sub-areas within the room type. This means that the adjectives should be universal enough to describe any plausible subregion within the broader area defined by the room type.
3. Genre Influence: Include genre-specific adjectives to provide the specific atmosphere. These should be words that are often associated with the genre and help build a mental picture of it. For example, 'post-apocalyptic' could inspire words like 'ruined', 'desolate', 'abandoned'.
4. Adjective Complexity & Connotation: Ensure a mix of positive, negative, and neutral descriptors, avoiding any overly exaggerated or unfitting terms. This involves avoiding words that would be too extreme for the room type or not align with the genre.
5. Compound Frequency & Type-specificity: Include a mix of single-word and compound adjectives, with some specifically suitable for the room environment. These should not dominate the list but rather provide additional variety and richness to the description.
6. The total number of adjectives generated per room type and genre should be 30, with one-third being ordinary universal adjectives and the rest being a blend of room-specific and genre-specific adjectives.
7. Output Format: The generated adjectives should be output as a JSON array of strings. Each string represents a single adjective or a compound adjective. The total number of adjectives in the array should be 30, with one-third being ordinary universal adjectives and the rest being a blend of room-specific and genre-specific adjectives.

For scenic descriptions:
1. Avoid Specific References: Describe the scenic objects or elements without directly mentioning specific room types, areas, or prompt-related words.
2. Diverse Sentence Structures: Use a variety of sentence structures to bring variety and interest to the descriptions.
3. Stay within the Genre: Ensure that the descriptions align with the overall thematic subject, such as the post-apocalyptic genre.
4. Compatibility with Theme: Maintain compatibility with the overall theme by depicting the appropriate atmosphere, mood, and ambiance.
5. Logical Consistency: Avoid referencing objects or elements that contradict the logic of the other rules or break the immersion of the scene.
6. Omit Time References: Do not mention the time of day by referencing the sun, moon, or stars in order to maintain a timeless quality.
7. Formatting: Format the output as a JSON array of comma-separated string values in quotes.

For atmospheric descriptions:
1. Atmospheric Focus: Descriptions should focus on evoking a moody, dramatic, and vivid atmosphere, putting emphasis on how the reader might feel within the space.
2. Wholeness of Atmosphere: Each generated statement should create a standalone impression of the atmosphere, independent of specific scenic elements.
3. Non-Visual Sensory Descriptions: Descriptions should extensively utilize non-visual sensory details, including smell, taste, sound, and feeling, to provide a richer sense of the atmosphere.
4. Expressive Detail: Descriptions should be detailed and expressive, avoiding ostentatious or overly flowery language. The aim is to evoke a vivid sense of place without distracting from the overall atmosphere.
5. Avoid Specific Scenic Elements: Refrain from referencing specific scenic objects or elements. Focus instead on creating an atmospheric impression.
6. Genre Adherence: Ensure the descriptions adhere to the specific genre and room type indicated in the prompt.
7. State of Place: Capture the relevant states of disrepair, abandonment, or other atmospheres associated with the genre and room type. 8. Consider the context and adjust the description to reflect the condition of the place.
9. Logical Consistency: Avoid referencing objects or elements that contradict the logic of the other rules or break the immersion of the scene.
Output Format: Format the output as a JSON array of comma-separated string values in quotes.



