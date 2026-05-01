"""
Generate remaining Middle East, Caucasus, East Asia, and Central Asia figures.
9 cultures x 20 figures = 180 figures
"""

from figure_factory import C, L, R, U, save

zoroastrian = [
    L("Ahura Mazda", "god", ["light", "wisdom", "creation", "fire"]),
    L("Angra Mainyu", "demon", ["darkness", "destruction", "death", "chaos"]),
    R("Spenta Mainyu", "spirit", ["light", "spirit", "creation", "truth"]),
    R("Anahita", "goddess", ["water", "fertility", "healing", "wisdom"]),
    R("Mithra", "god", ["sun", "justice", "light", "war"]),
    R("Atar", "god", ["fire", "purification", "light", "spirit"]),
    R("Verethragna", "god", ["war", "victory", "fire", "animal"]),
    R("Tishtrya", "spirit", ["rain", "star", "water", "light"]),
    U("Sraosha", "spirit", ["wisdom", "spirit", "justice", "night"]),
    U("Rashnu", "god", ["justice", "truth", "death", "wisdom"]),
    U("Haoma", "spirit", ["healing", "fertility", "spirit", "wisdom"]),
    U("Vayu-Vata", "god", ["wind", "sky", "war", "death"]),
    U("Haurvatat", "goddess", ["water", "healing", "wholeness", "light"]),
    U("Ameretat", "goddess", ["fertility", "life", "plants", "light"]),
    C("Fravashi", "spirit", ["ancestor", "light", "protection", "spirit"]),
    C("Daena", "spirit", ["wisdom", "soul", "judgment", "light"]),
    C("Chinvat Bridge", "guardian", ["justice", "death", "spirit", "threshold"]),
    C("Yima", "hero", ["kingship", "earth", "order", "sun"]),
    C("Keresaspa", "hero", ["war", "dragon", "strength", "fire"]),
    U("Simurgh", "creature", ["sky", "wisdom", "healing", "animal"]),
]
save("zoroastrian-persian", "Zoroastrian (Persian)", zoroastrian)

arabian = [
    L("al-Lat", "goddess", ["fertility", "earth", "light", "fate"]),
    L("al-Uzza", "goddess", ["war", "star", "power", "desert"]),
    R("Manat", "goddess", ["fate", "death", "time", "wisdom"]),
    R("Hubal", "god", ["divination", "war", "sky", "kingship"]),
    R("Dhu al-Shara", "god", ["mountain", "wine", "storm", "kingship"]),
    R("Quzah", "god", ["rain", "storm", "sky", "bow"]),
    R("Wadd", "god", ["love", "moon", "friendship", "oath"]),
    R("Nasr", "god", ["animal", "sky", "ancestor", "protection"]),
    U("Suwa", "goddess", ["beauty", "fertility", "water", "light"]),
    U("Yaghuth", "creature", ["animal", "war", "protection", "power"]),
    U("Ya'uq", "creature", ["animal", "speed", "mountain", "strength"]),
    U("Isaf", "spirit", ["stone", "pilgrimage", "oath", "desert"]),
    U("Na'ila", "spirit", ["love", "stone", "fate", "warning"]),
    U("Jinn", "spirit", ["spirit", "wind", "fire", "desert"]),
    C("Ifrit", "demon", ["fire", "darkness", "war", "spirit"]),
    C("Marid", "spirit", ["sea", "wind", "power", "spirit"]),
    C("Ghoul", "monster", ["death", "night", "desert", "hunger"]),
    C("Si'lat", "spirit", ["trickster", "desert", "shapechanging", "night"]),
    C("Qareen", "spirit", ["shadow", "spirit", "temptation", "fate"]),
    U("Ruda", "god", ["wind", "protection", "desert", "justice"]),
]
save("arabian-pre-islamic", "Arabian (Pre-Islamic)", arabian)

hittite = [
    L("Tarhunt", "god", ["storm", "war", "sky", "kingship"]),
    L("Arinna Sun Goddess", "goddess", ["sun", "light", "justice", "kingship"]),
    R("Teshub", "god", ["storm", "thunder", "mountain", "war"]),
    R("Hepat", "goddess", ["sky", "kingship", "motherhood", "light"]),
    R("Telepinu", "god", ["fertility", "agriculture", "earth", "spring"]),
    R("Kumarbi", "god", ["earth", "creation", "kingship", "darkness"]),
    R("Inara", "goddess", ["war", "animal", "hunt", "protection"]),
    R("Kamrusepa", "goddess", ["healing", "magic", "fire", "wisdom"]),
    U("Hannahannah", "goddess", ["wisdom", "motherhood", "fate", "earth"]),
    U("Illuyanka", "monster", ["serpent", "storm", "chaos", "mountain"]),
    U("Lelwani", "goddess", ["underworld", "death", "justice", "earth"]),
    U("Shaushka", "goddess", ["love", "war", "magic", "star"]),
    U("Ullikummi", "monster", ["mountain", "stone", "destruction", "darkness"]),
    U("Hedammu", "monster", ["sea", "serpent", "hunger", "chaos"]),
    C("Upelluri", "giant", ["earth", "mountain", "support", "stone"], alignment="neutral"),
    C("Pirwa", "god", ["animal", "horse", "war", "road"]),
    C("Zaliyanu", "goddess", ["river", "water", "fertility", "storm"]),
    C("Kurunta", "god", ["animal", "hunting", "mountain", "forest"]),
    C("Iyarri", "god", ["plague", "war", "arrow", "darkness"]),
    U("Taru", "creature", ["bull", "storm", "strength", "sky"]),
]
save("hittite", "Hittite", hittite)

assyrian = [
    L("Ashur", "god", ["war", "kingship", "sky", "justice"]),
    L("Ishtar of Nineveh", "goddess", ["war", "love", "star", "power"]),
    R("Nabu", "god", ["wisdom", "writing", "fate", "light"]),
    R("Ninurta", "god", ["war", "hunting", "storm", "earth"]),
    R("Shamash", "god", ["sun", "justice", "light", "wisdom"]),
    R("Adad", "god", ["storm", "rain", "war", "sky"]),
    R("Sin", "god", ["moon", "wisdom", "night", "fate"]),
    R("Mullissu", "goddess", ["kingship", "motherhood", "earth", "protection"]),
    U("Nergal", "god", ["underworld", "war", "plague", "fire"]),
    U("Ereshkigal", "goddess", ["underworld", "death", "darkness", "judgment"]),
    U("Tammuz", "god", ["fertility", "death", "spring", "agriculture"]),
    U("Lamassu", "guardian", ["protection", "sky", "animal", "kingship"]),
    U("Apkallu", "ancestor", ["wisdom", "water", "magic", "craft"]),
    U("Pazuzu", "demon", ["wind", "plague", "desert", "darkness"]),
    C("Lamashtu", "demon", ["plague", "night", "monster", "death"]),
    C("Anzu", "monster", ["storm", "sky", "theft", "animal"]),
    C("Etana", "hero", ["sky", "kingship", "eagle", "quest"]),
    C("Gilgamesh", "hero", ["war", "kingship", "strength", "quest"]),
    C("Utnapishtim", "ancestor", ["water", "wisdom", "survival", "fate"]),
    U("Nisroch", "god", ["agriculture", "storm", "protection", "forest"]),
]
save("assyrian", "Assyrian", assyrian)

yazidi = [
    L("Tawuse Melek", "angel", ["light", "spirit", "rainbow", "wisdom"], alignment="light"),
    L("Sheikh Adi", "saint", ["light", "spirit", "order", "healing"], alignment="light"),
    R("Sultan Ezid", "hero", ["kingship", "light", "justice", "spirit"], alignment="light"),
    R("Sheikh Hasan", "saint", ["wisdom", "spirit", "justice", "light"], alignment="light"),
    R("Shamsadin", "angel", ["sun", "light", "fire", "wisdom"], alignment="light"),
    R("Fakhradin", "angel", ["light", "wisdom", "music", "spirit"], alignment="light"),
    R("Nasirdin", "angel", ["death", "judgment", "spirit", "truth"], alignment="neutral"),
    R("Sajadin", "angel", ["protection", "spirit", "earth", "light"], alignment="light"),
    U("Xwede", "god", ["creation", "light", "wisdom", "sky"], alignment="light"),
    U("Heft Sirr", "spirit", ["spirit", "light", "mystery", "order"], alignment="light"),
    U("Khatuna Fakhra", "saint", ["fertility", "healing", "light", "water"], alignment="light"),
    U("Pire Fat", "ancestor", ["ancestor", "light", "wisdom", "mercy"], alignment="light"),
    U("Pire Liban", "ancestor", ["spirit", "protection", "ritual", "light"], alignment="light"),
    U("Derwesh e Evdi", "hero", ["quest", "spirit", "love", "mountain"], alignment="neutral"),
    C("Melek Sheikh Sin", "angel", ["moon", "light", "spirit", "night"], alignment="light"),
    C("Melek Shexubakr", "angel", ["justice", "light", "wisdom", "oath"], alignment="light"),
    C("Melek Sicadin", "angel", ["earth", "protection", "spirit", "light"], alignment="light"),
    C("Melek Nasirdin", "angel", ["death", "judgment", "spirit", "light"], alignment="neutral"),
    C("Melek Fakhradin", "angel", ["music", "spirit", "light", "wisdom"], alignment="light"),
    U("Lalish Guardian", "guardian", ["earth", "spirit", "light", "sanctuary"], alignment="light"),
]
save("yazidi", "Yazidi", yazidi)

georgian = [
    L("Amirani", "hero", ["fire", "mountain", "rebellion", "strength"]),
    L("Satanaya", "goddess", ["wisdom", "motherhood", "magic", "fate"]),
    R("Sosruko", "hero", ["fire", "trickster", "war", "speed"]),
    R("Batraz", "hero", ["storm", "iron", "war", "sky"]),
    R("Uryzmag", "hero", ["kingship", "war", "wisdom", "honor"]),
    R("Tlepsh", "god", ["iron", "craft", "fire", "wisdom"]),
    R("Syrdon", "spirit", ["trickster", "music", "shadow", "wit"]),
    R("Dali", "goddess", ["animal", "mountain", "hunting", "beauty"]),
    U("Khamyts", "hero", ["war", "horse", "honor", "strength"]),
    U("Atsamaz", "hero", ["music", "love", "spirit", "nature"]),
    U("Mindia", "hero", ["forest", "wisdom", "animal", "healing"]),
    U("Kopala", "god", ["storm", "war", "mountain", "justice"]),
    U("Iakhsar", "god", ["war", "hunting", "mountain", "protection"]),
    U("Samdzimari", "spirit", ["mountain", "fertility", "love", "light"]),
    C("Ochokochi", "monster", ["forest", "monster", "hunting", "night"]),
    C("Gveleshapi", "monster", ["dragon", "water", "mountain", "chaos"]),
    C("Devi", "monster", ["mountain", "darkness", "strength", "chaos"]),
    C("Ali", "spirit", ["storm", "wind", "mountain", "night"]),
    C("Tetri Giorgi", "hero", ["light", "war", "horse", "protection"]),
    U("Paskunji", "creature", ["sky", "mountain", "rescue", "animal"]),
]
save("georgian-nart", "Georgian / Caucasian (Nart Sagas)", georgian)

armenian = [
    L("Aramazd", "god", ["creation", "sky", "fertility", "wisdom"]),
    L("Vahagn", "god", ["fire", "war", "dragon", "storm"]),
    R("Anahit", "goddess", ["fertility", "healing", "wisdom", "water"]),
    R("Astghik", "goddess", ["love", "water", "beauty", "light"]),
    R("Mihr", "god", ["sun", "light", "justice", "oath"]),
    R("Nane", "goddess", ["war", "wisdom", "protection", "kingship"]),
    R("Tir", "god", ["wisdom", "writing", "fate", "moon"]),
    R("Spandaramet", "goddess", ["underworld", "earth", "death", "fertility"]),
    U("Barshamin", "god", ["sky", "storm", "light", "kingship"]),
    U("Amanor", "god", ["time", "harvest", "hospitality", "earth"]),
    U("Vanatur", "god", ["hospitality", "earth", "travel", "abundance"]),
    U("Ara the Beautiful", "hero", ["beauty", "kingship", "war", "fate"]),
    U("Shamiram", "goddess", ["kingship", "love", "war", "ambition"]),
    U("Hayk", "hero", ["war", "archery", "ancestor", "freedom"]),
    C("Aralez", "creature", ["healing", "animal", "death", "resurrection"]),
    C("Vishap", "monster", ["dragon", "water", "mountain", "chaos"]),
    C("Torq Angegh", "hero", ["strength", "war", "earth", "giant"]),
    C("David of Sassoun", "hero", ["war", "horse", "strength", "justice"]),
    C("Mher", "hero", ["sun", "war", "gate", "fate"]),
    U("Tsovinar", "goddess", ["sea", "storm", "water", "fertility"]),
]
save("armenian", "Armenian", armenian)

buryat = [
    L("Geser", "hero", ["war", "sky", "spirit", "kingship"]),
    L("Esege Malan", "god", ["sky", "creation", "light", "wisdom"]),
    R("Manzan Gurme", "goddess", ["wisdom", "spirit", "ancestor", "earth"]),
    R("Atai Ulaan", "demon", ["war", "darkness", "chaos", "storm"]),
    R("Khan Khormusta", "god", ["sky", "justice", "light", "kingship"]),
    R("Abai Geser", "hero", ["war", "mountain", "horse", "victory"]),
    R("Sagaan Ubugen", "ancestor", ["wisdom", "ancestor", "fertility", "light"]),
    R("Bukhe Belligte", "hero", ["strength", "war", "earth", "honor"]),
    U("Solbon", "spirit", ["star", "light", "sky", "guidance"]),
    U("Zasa Mergen", "hero", ["archery", "hunting", "wisdom", "speed"]),
    U("Abai Khatan", "goddess", ["light", "fate", "beauty", "spirit"]),
    U("Mayas Hara", "goddess", ["darkness", "fate", "earth", "spirit"]),
    U("Galta Ulaan", "demon", ["fire", "war", "chaos", "storm"]),
    U("Azhirai Bukhe", "monster", ["monster", "strength", "darkness", "mountain"]),
    C("Shanaihan Shara", "spirit", ["spirit", "ritual", "wisdom", "healing"]),
    C("Uha Loson", "god", ["water", "wisdom", "spirit", "lake"]),
    C("Burkhan Khaldun Spirit", "guardian", ["mountain", "spirit", "ancestor", "protection"]),
    C("Tenger Rider", "spirit", ["sky", "wind", "war", "spirit"]),
    C("Blue Wolf Ancestor", "creature", ["ancestor", "animal", "speed", "protection"]),
    U("White Shaman Drum", "spirit", ["spirit", "sky", "rhythm", "healing"]),
]
save("buryat-mongol", "Buryat Mongol", buryat)

taiwanese = [
    L("Kakacawan Sapatrok", "ancestor", ["ancestor", "earth", "spirit", "origin"]),
    L("Kawas", "spirit", ["spirit", "forest", "ancestor", "mystery"]),
    R("Princess Baleng", "heroine", ["love", "lake", "fate", "mountain"]),
    R("Snake King Adalio", "creature", ["serpent", "water", "mountain", "protection"]),
    R("Cidal", "god", ["sun", "light", "sky", "ancestor"]),
    R("Fasonihar", "god", ["protection", "spirit", "earth", "harvest"]),
    R("Faydongi", "spirit", ["harvest", "ancestor", "earth", "light"]),
    R("Kavulungan", "guardian", ["mountain", "ancestor", "earth", "sanctuary"]),
    U("Mahahan", "god", ["sea", "storm", "wind", "water"]),
    U("Mariyaru", "spirit", ["sea", "water", "spirit", "rain"]),
    U("Marimokoshi", "spirit", ["sea", "storm", "darkness", "wind"]),
    U("Kosomatora", "spirit", ["sea", "water", "guidance", "sky"]),
    U("Dilukai", "guardian", ["fertility", "earth", "protection", "ancestor"]),
    U("Alikakay", "giant", ["strength", "mountain", "forest", "earth"]),
    C("Hanido", "spirit", ["spirit", "ancestor", "forest", "earth"]),
    C("Tjukutjuku", "ancestor", ["origin", "earth", "family", "mountain"]),
    C("Pulalulaluyan", "ancestor", ["origin", "family", "earth", "ancestor"]),
    C("Hundred-Pacer Spirit", "creature", ["serpent", "ancestor", "mountain", "protection"]),
    C("Sea Winds", "spirit", ["wind", "sea", "travel", "guidance"]),
    U("Millet Song Keeper", "ancestor", ["harvest", "music", "ancestor", "earth"]),
]
save("taiwanese-aboriginal", "Taiwanese Aboriginal (Formosan)", taiwanese)

print("\nFrontier figures complete.")
print("Total: 9 cultures x 20 figures = 180 figures")
