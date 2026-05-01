"""
Generate Oceania figures.
8 cultures x 20 figures = 160 figures
"""

from figure_factory import C, L, R, U, save

hawaiian = [
    L("Kane", "god", ["creation", "light", "water", "life"]),
    L("Pele", "goddess", ["fire", "volcano", "destruction", "passion"]),
    R("Kanaloa", "god", ["sea", "underworld", "healing", "magic"]),
    R("Ku", "god", ["war", "kingship", "strength", "forest"]),
    R("Lono", "god", ["fertility", "rain", "peace", "agriculture"]),
    R("Hi'iaka", "goddess", ["healing", "hula", "forest", "light"]),
    R("Maui", "hero", ["sun", "trickster", "sea", "quest"]),
    R("Namaka", "goddess", ["sea", "water", "storm", "revenge"]),
    U("Kamapua'a", "hero", ["animal", "fertility", "forest", "rain"]),
    U("Poli'ahu", "goddess", ["ice", "mountain", "snow", "light"]),
    U("Hina", "goddess", ["moon", "wisdom", "craft", "light"]),
    U("Wakea", "god", ["sky", "creation", "ancestor", "kingship"]),
    U("Papahanaumoku", "goddess", ["earth", "creation", "motherhood", "fertility"]),
    U("Kamohoalii", "god", ["sea", "shark", "storm", "animal"]),
    C("Haumea", "goddess", ["fertility", "earth", "motherhood", "light"]),
    C("La'amaomao", "spirit", ["wind", "sky", "guidance", "storm"]),
    C("Kihawahine", "spirit", ["water", "protection", "lizard", "royalty"]),
    C("Nanaue", "monster", ["shark", "sea", "monster", "hunger"]),
    C("Mo'o Inanea", "spirit", ["water", "lizard", "illusion", "protection"]),
    U("Milu", "god", ["underworld", "death", "darkness", "spirit"]),
]
save("hawaiian-polynesian", "Hawaiian Polynesian", hawaiian)

maori = [
    L("Tane Mahuta", "god", ["forest", "creation", "light", "sky"]),
    L("Maui", "hero", ["trickster", "sun", "sea", "quest"]),
    R("Tangaroa", "god", ["sea", "water", "animal", "creation"]),
    R("Tawhirimatea", "god", ["storm", "wind", "sky", "war"]),
    R("Tu Matauenga", "god", ["war", "strength", "kingship", "justice"]),
    R("Rongo", "god", ["fertility", "peace", "agriculture", "earth"]),
    R("Ruaumoko", "god", ["earth", "fire", "quake", "underworld"]),
    R("Hine-nui-te-po", "goddess", ["death", "night", "underworld", "spirit"]),
    U("Ranginui", "god", ["sky", "rain", "creation", "light"]),
    U("Papatuanuku", "goddess", ["earth", "fertility", "creation", "motherhood"]),
    U("Haumia-tiketike", "god", ["roots", "fertility", "earth", "agriculture"]),
    U("Hina", "goddess", ["moon", "wisdom", "craft", "water"]),
    U("Whaitiri", "goddess", ["thunder", "storm", "war", "sky"]),
    U("Uenuku", "god", ["rainbow", "war", "sky", "omen"]),
    C("Tinirau", "god", ["sea", "fish", "abundance", "water"]),
    C("Rehua", "god", ["star", "healing", "light", "wisdom"]),
    C("Tiki", "ancestor", ["creation", "ancestor", "earth", "life"]),
    C("Rona", "spirit", ["moon", "water", "night", "fate"]),
    C("Pania", "spirit", ["sea", "love", "water", "beauty"]),
    U("Taniwha", "creature", ["water", "serpent", "guardian", "monster"]),
]
save("maori", "Maori (New Zealand)", maori)

samoan = [
    L("Tagaloa", "god", ["creation", "sky", "sea", "light"]),
    L("Nafanua", "goddess", ["war", "prophecy", "justice", "kingship"]),
    R("Saveasi'uleo", "god", ["underworld", "spirit", "darkness", "fate"]),
    R("Taema", "spirit", ["tattoo", "craft", "water", "wisdom"]),
    R("Tilafaiga", "spirit", ["tattoo", "war", "craft", "trickster"]),
    R("Sina", "heroine", ["moon", "love", "water", "beauty"]),
    R("Tigilau", "hero", ["sea", "voyage", "love", "kingship"]),
    R("Ti'iti'i", "hero", ["fire", "trickster", "quest", "strength"]),
    U("Mafui'e", "god", ["fire", "underworld", "storm", "power"]),
    U("Pili", "hero", ["voyage", "kingship", "ancestor", "sea"]),
    U("Tui Fiti", "hero", ["sea", "challenge", "kingship", "honor"]),
    U("Le Sa", "spirit", ["sacred", "taboo", "judgment", "spirit"]),
    U("Moso", "hero", ["strength", "voyage", "trickster", "animal"]),
    U("Aitu", "spirit", ["spirit", "night", "ancestor", "mystery"]),
    C("Tuna", "creature", ["water", "shapechanging", "love", "moon"]),
    C("Pulotu Keeper", "guardian", ["underworld", "spirit", "threshold", "night"]),
    C("Aloalo", "hero", ["sun", "light", "youth", "sky"]),
    C("Nifoloa", "monster", ["monster", "night", "serpent", "darkness"]),
    C("Coconut Eel", "creature", ["water", "fertility", "animal", "sacrifice"]),
    U("Falealupo Gate", "guardian", ["underworld", "wind", "spirit", "sea"]),
]
save("samoan", "Samoan", samoan)

tongan = [
    L("Tangaloa 'Eitumatupua", "god", ["sky", "creation", "kingship", "light"]),
    L("Hikule'o", "goddess", ["underworld", "spirit", "fertility", "power"]),
    R("Maui Kisikisi", "hero", ["trickster", "sun", "sea", "quest"]),
    R("Maui Atalanga", "hero", ["strength", "sea", "voyage", "family"]),
    R("Hina", "goddess", ["moon", "beauty", "wisdom", "water"]),
    R("Aho'eitu", "hero", ["sky", "kingship", "ancestor", "honor"]),
    R("Havea Hikule'o", "god", ["underworld", "storm", "darkness", "earth"]),
    R("Sinilau", "god", ["sea", "abundance", "love", "water"]),
    U("Lau-fakanaa", "hero", ["voyage", "trickster", "sea", "wisdom"]),
    U("Kae", "hero", ["trickster", "theft", "sea", "speech"]),
    U("Lata", "hero", ["voyage", "craft", "forest", "quest"]),
    U("Toloa", "creature", ["bird", "voyage", "sky", "guidance"]),
    U("Pulotu Keeper", "guardian", ["underworld", "spirit", "threshold", "night"]),
    U("Ilaheva", "heroine", ["love", "kingship", "sea", "beauty"]),
    C("Niuhi", "monster", ["shark", "sea", "monster", "hunger"]),
    C("Lupe", "spirit", ["bird", "messenger", "sky", "guidance"]),
    C("Talatupou", "hero", ["voyage", "honor", "sea", "strength"]),
    C("Tafakula", "creature", ["sea", "animal", "storm", "fury"]),
    C("Tongahiti", "ancestor", ["ancestor", "voyage", "kingship", "earth"]),
    U("Kau'ulufonua", "hero", ["kingship", "justice", "war", "earth"]),
]
save("tongan", "Tongan", tongan)

aboriginal = [
    L("Rainbow Serpent", "creature", ["serpent", "water", "creation", "earth"]),
    L("Baiame", "god", ["sky", "creation", "wisdom", "law"]),
    R("Bunjil", "god", ["sky", "light", "eagle", "creation"]),
    R("Yhi", "goddess", ["sun", "light", "creation", "fire"]),
    R("Daramulum", "god", ["sky", "law", "initiation", "justice"]),
    R("Wandjina", "spirit", ["rain", "cloud", "storm", "sky"]),
    R("Tiddalik", "monster", ["water", "hunger", "earth", "monster"]),
    R("Julunggul", "creature", ["serpent", "water", "fertility", "spirit"]),
    U("Mamaragan", "god", ["lightning", "storm", "sky", "fire"]),
    U("Mimi", "spirit", ["spirit", "art", "wind", "forest"]),
    U("Namorrodor", "monster", ["night", "death", "monster", "shadow"]),
    U("Kunapipi", "goddess", ["fertility", "earth", "ritual", "life"]),
    U("Ungud", "creature", ["serpent", "water", "creation", "spirit"]),
    U("Gnowee", "goddess", ["sun", "light", "motherhood", "sky"]),
    C("Bahloo", "god", ["moon", "night", "water", "sky"]),
    C("Kidili", "hero", ["moon", "fire", "trickster", "wandering"]),
    C("Wati Kutjara", "hero", ["journey", "desert", "brotherhood", "quest"]),
    C("Wawalag Sisters", "spirit", ["fertility", "ritual", "serpent", "song"]),
    C("Akurra", "creature", ["serpent", "mountain", "earth", "power"]),
    U("Altjira", "god", ["sky", "ancestor", "dream", "creation"]),
]
save("aboriginal-australian", "Aboriginal Australian (Dreamtime)", aboriginal)

melanesian = [
    L("Qat", "hero", ["creation", "trickster", "light", "craft"]),
    L("Tagaro", "god", ["creation", "sky", "war", "kingship"]),
    R("Marawa", "spirit", ["trickster", "spider", "wisdom", "speed"]),
    R("Vinmara", "goddess", ["love", "fertility", "earth", "beauty"]),
    R("To Kabinana", "hero", ["creation", "wisdom", "light", "craft"]),
    R("To Karvuvu", "spirit", ["darkness", "death", "chaos", "trickster"]),
    R("Hatuibwari", "creature", ["serpent", "sea", "creation", "power"]),
    R("Agunua", "god", ["serpent", "sun", "sea", "animal"]),
    U("Abere", "spirit", ["night", "underworld", "monster", "darkness"]),
    U("Adaro", "spirit", ["sea", "storm", "sun", "spirit"]),
    U("Kakamora", "creature", ["forest", "trickster", "animal", "night"]),
    U("Suqe-Matua", "ancestor", ["ritual", "ancestor", "wisdom", "order"]),
    U("Mansren", "hero", ["prophecy", "light", "justice", "hope"]),
    U("Aiwel", "spirit", ["forest", "spirit", "healing", "mystery"]),
    C("Moroa", "spirit", ["sea", "ancestor", "storm", "guidance"]),
    C("Vele", "spirit", ["forest", "fertility", "earth", "protection"]),
    C("Sambali", "hero", ["voyage", "sea", "quest", "courage"]),
    C("Tambaran Mask", "guardian", ["spirit", "ritual", "ancestor", "fear"]),
    C("Crocodile Ancestor", "creature", ["water", "ancestor", "animal", "earth"]),
    U("Bird of Paradise Spirit", "spirit", ["bird", "light", "beauty", "sky"]),
]
save("melanesian-papuan", "Melanesian / Papuan", melanesian)

chamorro = [
    L("Puntan", "god", ["creation", "sky", "sacrifice", "light"]),
    L("Fu'una", "goddess", ["creation", "earth", "motherhood", "sea"]),
    R("Chaife", "demon", ["storm", "fire", "wind", "darkness"]),
    R("Gadao", "hero", ["strength", "kingship", "war", "honor"]),
    R("Taotaomo'na", "spirit", ["ancestor", "forest", "earth", "spirit"]),
    R("Sirena", "spirit", ["sea", "water", "beauty", "warning"]),
    R("Mataquana", "hero", ["war", "challenge", "honor", "strength"]),
    R("Makana", "spirit", ["magic", "healing", "wisdom", "ritual"]),
    U("Malaguana", "heroine", ["love", "sea", "fate", "beauty"]),
    U("Suruhanu", "spirit", ["healing", "ritual", "wisdom", "ancestor"]),
    U("Tuyong", "spirit", ["wind", "sea", "guidance", "sky"]),
    U("Fouha Spirit", "guardian", ["earth", "sea", "ancestor", "sanctuary"]),
    U("Laso de Fua", "guardian", ["stone", "ancestor", "earth", "endurance"]),
    U("Dos Amantes", "spirit", ["love", "fate", "cliff", "sea"]),
    C("Tuba Gatherer", "ancestor", ["ancestor", "craft", "earth", "abundance"]),
    C("Bird of Luta", "creature", ["bird", "sky", "guidance", "sea"]),
    C("Latte Guardian", "guardian", ["stone", "ancestor", "protection", "earth"]),
    C("Moon over Hagatna", "spirit", ["moon", "water", "night", "guidance"]),
    C("Island Shark Spirit", "creature", ["sea", "animal", "protection", "storm"]),
    U("Aniti Keeper", "spirit", ["spirit", "ancestor", "ritual", "protection"]),
]
save("chamorro-micronesian", "Chamorro / Micronesian", chamorro)

fijian = [
    L("Degei", "god", ["serpent", "creation", "earth", "judgment"]),
    L("Dakuwaqa", "god", ["shark", "sea", "storm", "war"]),
    R("Rokobakaniceva", "goddess", ["sea", "octopus", "protection", "water"]),
    R("Ratumaibulu", "god", ["fertility", "earth", "underworld", "agriculture"]),
    R("Lutunasobasoba", "hero", ["voyage", "ancestor", "sea", "leadership"]),
    R("Tavatavaimasi", "spirit", ["craft", "wisdom", "ritual", "fire"]),
    R("Kacikaaumoli", "spirit", ["trickster", "earth", "night", "magic"]),
    R("Bui Kalou", "goddess", ["spirit", "ancestor", "forest", "earth"]),
    U("Rokola", "hero", ["serpent", "strength", "mountain", "honor"]),
    U("Kaunitoni Spirit", "guardian", ["voyage", "sea", "ancestor", "guidance"]),
    U("Tui Delai Gau", "god", ["sea", "island", "kingship", "storm"]),
    U("Qiolevu", "creature", ["serpent", "water", "monster", "power"]),
    U("Bitu-ni-valu", "spirit", ["war", "ancestor", "ritual", "honor"]),
    U("Ndengei's Judge", "guardian", ["judgment", "underworld", "stone", "spirit"]),
    C("Yalo Spirit", "spirit", ["ancestor", "spirit", "night", "guidance"]),
    C("Firewalker of Beqa", "hero", ["fire", "ritual", "courage", "earth"]),
    C("Cakau Guardian", "guardian", ["reef", "sea", "protection", "animal"]),
    C("Turtle Messenger", "creature", ["sea", "animal", "guidance", "wisdom"]),
    C("Yaqona Keeper", "spirit", ["ritual", "healing", "wisdom", "earth"]),
    U("Storm Canoe Ancestor", "ancestor", ["voyage", "storm", "ancestor", "sea"]),
]
save("fijian", "Fijian", fijian)

print("\nOceania figures complete.")
print("Total: 8 cultures x 20 figures = 160 figures")
