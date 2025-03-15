// -------------------ARMOR RULES------------------------
// Normal Armor = 1 "block" of Armor
// Beacons = .5 "blocks" of Armor

// ---"Essensal" room RULES---
// SHL must have 6 blocks of armor
RULE "SHL_ARMOR"
    WHEN
        // SHL has less than 6 blocks of armor
        room.short_name == "SHL" && room.armor < 15
    THEN
        penalty(-5),
        message("SHL must have 15 blocks of armor")