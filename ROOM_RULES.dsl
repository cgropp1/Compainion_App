// -------------------ARMOR RULES------------------------
// Normal Armor = 1 "block" of Armor
// Beacons = .5 "blocks" of Armor

// ---"Essensal" room RULES---
// SHL must have 6 blocks of armor
RULE "SHL_ARMOR"
    WHEN
        // SHL has less than 6 blocks of armor
        room.short_name == "SHL" && room.armor <= (6*self.ship_armor_value)
    THEN
        penalty(-5),
        message("SHL must have 6 blocks of armor")

// TLP must have 6 blocks of armor
RULE "TLP_ARMOR"
    WHEN
        // TLP has less than 6 blocks of armor
        room.type == "TLP" && room.armor <= (6*self.ship_armor_value)
    THEN
        penalty(-5),
        message("TLP must have 6 blocks of armor")

// MML must have 6 blocks of armor
RULE "MML_ARMOR"
    WHEN
        // MML has less than 6 blocks of armor
        room.type == "MML" && room.armor <= (6*self.ship_armor_value)
    THEN
        penalty(-5),
        message("MML must have 6 blocks of armor")

// BT must have 5 blocks of armor (minimum of 4)
RULE "BT_ARMOR"
    WHEN
        // BT has less than 5 blocks of armor
        room.type == "BT" && room.armor <= (5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("BT should have 5 blocks of armor")
RULE "BT_ARMOR_MIN"
    WHEN
        // BT has less than 4 blocks of armor
        room.type == "BT" && room.armor <= (4*self.ship_armor_value)
    THEN
        penalty(-4),
        message("BT must have a minimum of 4 blocks of armor")

// AS must have 5 blocks of armor (minimum of 4)
RULE "AS_ARMOR"
    WHEN
        // AS has less than 5 blocks of armor
        room.type == "AS" && room.armor <= (5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("AS should have 5 blocks of armor")
RULE "AS_ARMOR_MIN"
    WHEN
        // AS has less than 4 blocks of armor
        room.type == "AS" && room.armor <= (4*self.ship_armor_value)
    THEN
        penalty(-4),
        message("AS must have a minimum of 4 blocks of armor")

// MD must have 5 blocks of armor (minimum of 4)
RULE "MD_ARMOR"
    WHEN
        // MD has less than 5 blocks of armor
        room.type == "MD" && room.armor <= (5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("MD should have 5 blocks of armor")
RULE "MD_ARMOR_MIN"
    WHEN
        // MD has less than 4 blocks of armor
        room.type == "MD" && room.armor <= (4*self.ship_armor_value)
    THEN
        penalty(-4),
        message("MD must have a minimum of 4 blocks of armor")

// AA must have 5 blocks of armor (minimum of 4)
RULE "AA_ARMOR"
    WHEN
        // AA has less than 5 blocks of armor
        room.type == "AA" && room.armor <= (5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("AA should have 5 blocks of armor")
RULE "AA_ARMOR_MIN"
    WHEN
        // AA has less than 4 blocks of armor
        room.type == "AA" && room.armor <= (4*self.ship_armor_value)
    THEN
        penalty(-4),
        message("AA must have a minimum of 4 blocks of armor")

// 2x2 rooms should have 5 armor (minimum of 4)
RULE "2x2_ARMOR"
    WHEN
        // 2x2 room has less than 5 blocks of armor
        room.size == [2,2] && room.armor <= (5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("2x2 rooms should have 5 blocks of armor")
RULE "2x2_ARMOR_MIN"
    WHEN
        // 2x2 room has less than 4 blocks of armor
        room.size == [2,2] && room.armor <= (4*self.ship_armor_value)
    THEN
        penalty(-4),
        message("2x2 rooms must have a minimum of 4 blocks of armor")

// ---"Non-Essensal" room RULES---
// MLZ should have 4 blocks of armor (minimum of 3)
RULE "MLZ_ARMOR"
    WHEN
        // MLZ has less than 4 blocks of armor
        room.type == "MLZ" && room.armor <= (4*self.ship_armor_value)
    THEN
        penalty(-.5),
        message("MLZ should have 4 blocks of armor")
RULE "MLZ_ARMOR_MIN"
    WHEN
        // MLZ has less than 3 blocks of armor
        room.type == "MLZ" && room.armor <= (3*self.ship_armor_value)
    THEN
        penalty(-2),
        message("MLZ must have a minimum of 3 blocks of armor")

// ENG should have 3 blocks of armor (minimum of 2.5)
RULE "ENG_ARMOR"
    WHEN
        // ENG has less than 3 blocks of armor
        room.type == "ENG" && room.armor <= (3*self.ship_armor_value)
    THEN
        penalty(-.5),
        message("ENG should have 3 blocks of armor")
RULE "ENG_ARMOR_MIN"
    WHEN
        // ENG has less than 2.5 blocks of armor
        room.type == "ENG" && room.armor <= (2.5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("ENG must have a minimum of 2.5 blocks of armor")

// MSL should have 3 blocks of armor (minimum of 2.5)
RULE "MSL_ARMOR"
    WHEN
        // MSL has less than 3 blocks of armor
        room.type == "MSL" && room.armor <= (3*self.ship_armor_value)
    THEN
        penalty(-.5),
        message("MSL should have 3 blocks of armor")
RULE "MSL_ARMOR_MIN"
    WHEN
        // MSL has less than 2.5 blocks of armor
        room.type == "MSL" && room.armor <= (2.5*self.ship_armor_value)
    THEN
        penalty(-1),
        message("MSL must have a minimum of 2.5 blocks of armor")

// REA should have 1 block of armor (minimum of .5) (maximum of 3)
RULE "REA_ARMOR"
    WHEN
        // REA has less than 1 block of armor
        room.type == "REA" && room.armor <= (1*self.ship_armor_value)
    THEN
        penalty(-.25),
        message("REA should have 1 block of armor")
RULE "REA_ARMOR_MIN"
    WHEN
        // REA has less than .5 blocks of armor
        room.type == "REA" && room.armor <= (.5*self.ship_armor_value)
    THEN
        penalty(-.5),
        message("REA must have a minimum of .5 blocks of armor")
RULE "REA_ARMOR_MAX"
    WHEN
        // REA has more than 3 blocks of armor
        room.type == "REA" && room.armor >= (3*self.ship_armor_value)
    THEN
        penalty(-1),
        message("REA must have a maximum of 3 blocks of armor")

// FEA should have 1 block of armor (minimum of .5) (maximum of 3)
RULE "FEA_ARMOR"
    WHEN
        // FEA has less than 1 block of armor
        room.type == "FEA" && room.armor <= (1*self.ship_armor_value)
    THEN
        penalty(-.25),
        message("FEA should have 1 block of armor")
RULE "FEA_ARMOR_MIN"
    WHEN
        // FEA has less than .5 blocks of armor
        room.type == "FEA" && room.armor <= (.5*self.ship_armor_value)
    THEN
        penalty(-.5),
        message("FEA must have a minimum of .5 blocks of armor")
RULE "FEA_ARMOR_MAX"
    WHEN
        // FEA has more than 3 blocks of armor
        room.type == "FEA" && room.armor >= (3*self.ship_armor_value)
    THEN
        penalty(-1),
        message("FEA must have a maximum of 3 blocks of armor")

// HAN should have mininal armor (maximum of 3)
RULE "HAN_ARMOR"
    WHEN
        // HAN has armor
        room.type == "HAN" && room.armor >= (3*self.ship_armor_value)
    THEN
        penalty(-.25),
        message("HAN should have minimal armor")

// DH should have mininal armor (maximum of 3)
RULE "DH_ARMOR"
    WHEN
        // DH has armor
        room.type == "DH" && room.armor >= (3*self.ship_armor_value)
    THEN
        penalty(-.25),
        message("DH should have minimal armor")

// Don't armor non-powered rooms
RULE "NON_POWERED_ARMOR"
    WHEN
        // Non-powered room has armor
        room.powered == False && room.armor >= 400
    THEN
        penalty(-.5),
        message("Non-powered rooms should not have armor")
RULE "NON_POWERED_ARMOR_MAX"
    WHEN
        // Non-powered room has armor
        room.powered == False && room.armor >= (400 + (2*self.ship_armor_value))
    THEN
        penalty(-5),
        message("Non-powered rooms should not have armor")