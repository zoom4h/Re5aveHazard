import os
import tkinter as tk
from time import sleep
from editor import RE5SaveData
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass, field

@dataclass
class D: # Ensure all D-classes has those two
    def read_value(self):
        pass

    def write_value(self):
        pass

@dataclass
class DSeparator(D):
    widget: None = None

    def create(self, parent, **kwargs):
        self.widget = ttk.Separator(
            parent,
            orient='horizontal',
            #style="TLabel",
            **kwargs
        )

@dataclass
class DLabel(D):
    text: str
    width: int = None
    widget: None = None

    def create(self, parent, **kwargs):
        self.widget = ttk.Label(
            parent,
            text=self.text,
            style="TLabel",
            width=self.width,
            **kwargs
        )

@dataclass
class DCheckbutton(D):
    offset: int
    bit_index: int = 0
    text: str = ''
    var: None = None
    widget: None = None

    def create(self, parent, **kwargs):
        self.var = tk.BooleanVar()
        self.widget = ttk.Checkbutton(
            parent,
            variable=self.var,
            text=self.text,
            style="TCheckbutton",
            **kwargs
        )
    
    def read_value(self):
        value = savedata.get_bit(self.offset, self.bit_index)
        self.var.set(value)

    def write_value(self):
        value = int(self.var.get())
        savedata.set_bit(self.offset, self.bit_index, value)

@dataclass
class DEntry(D):
    offset: int
    size: int = 1
    min: int = 0
    max: int = None
    width: int = 20
    var: None = None
    widget: None = None

    def __post_init__(self):
        if type(self.max) is not(int):
            self.max = 2 ** (self.size*8) - 1

    def create(self, parent, **kwargs):
        self.var = tk.IntVar()
        self.widget = ttk.Entry(
            parent,
            textvariable=self.var,
            style="TEntry",
            validate="key",
            width=self.width,
            **kwargs
        )
        validate_command = (self.widget.register(self.validate), '%P')
        self.widget.configure(validatecommand=validate_command)
    
    def validate(self, value):
        if value.isdigit():
            iv = int(value)
            if iv < self.min or iv > self.max:
                return False
            return True
        return False
    
    def read_value(self):
        value = savedata.get_value(self.offset, self.size)
        self.var.set(value)

    def write_value(self):
        value = int(self.var.get())
        savedata.set_value(value, self.offset, self.size)

@dataclass
class DCombobox(D):
    offset: int
    size: int = 1
    options: dict = field(default_factory=lambda: {'Default option 1': 0, 'Default option 2': 1})
    width: int = 20
    var: None = None
    widget: None = None

    def create(self, parent, **kwargs):
        self.var = tk.StringVar()
        self.widget = ttk.Combobox(
            parent,
            values=list(self.options.keys()),
            style="TCombobox",
            width=self.width,
            **kwargs
        )
        self.widget.bind("<<ComboboxSelected>>", self.select)
    
    def select(self, event):
        self.var.set(self.options[event.widget.get()])

    def read_value(self):
        if type(self.offset) in (tuple, list):
            chunks = bytes()
            for offset in self.offset:
                chunk = savedata.get_bytes(offset, self.size)
                chunks = bytes().join([chunks, chunk])
            value = int.from_bytes(chunks, 'little')

        elif type(self.offset) is int:
            value = savedata.get_value(self.offset, self.size)
            
        values = list(self.options.values())
        
        if value in values:
            self.widget.current(values.index(value))
        else:
            self.widget.set(f'{hex(value)}')
            
        self.widget.configure(state="readonly")
        self.var.set(value)

    def write_value(self):
        value = int(self.var.get())

        if type(self.offset) is int:
            savedata.set_value(value, self.offset, self.size) 

        elif type(self.offset) in (tuple, list):
            i = 0
            n = len(self.offset)
            chunks = value.to_bytes(n*self.size, 'little')

            for offset in self.offset:
                chunk = chunks[ i*self.size : (i+1)*self.size ]
                savedata.set_bytes(chunk, offset, self.size)
                i += 1

@dataclass
class DTabFrame(D):
    label: str
    content: list = field(default_factory=lambda: list())
    rowspan: int = 1
    colspan: int = 1
    uniform: bool = True
    widget: None = None

    def create(self, parent, frame_row, frame_col):
        self.content = frames.get(self.label)

        if self.content is None:
            raise ValueError(f'Frame "{self.label}" does not exist in "frames"')
        
        self.widget = ttk.LabelFrame(parent, text=self.label) # style='TFrame'
        self.widget.grid(row=frame_row, column=frame_col, rowspan=self.rowspan, columnspan=self.colspan, sticky='nesw', padx=5, pady=10)
        f_row_index = 0

        for f_row in self.content:
            f_col_index = 0

            for f_cell in f_row:

                if type(f_cell) in (DCheckbutton, DCombobox, DEntry, DLabel, DClick):
                    f_cell.create(self.widget, state="disabled")
                    if type(f_cell) is DLabel:
                        f_cell.widget.grid(row=f_row_index, column=f_col_index, padx=5, pady=2, sticky='w')
                    else:
                        f_cell.widget.grid(row=f_row_index, column=f_col_index, padx=2, pady=2, sticky='w')
                elif type(f_cell) is DSeparator:
                    f_cell.create(self.widget)
                    f_cell.widget.grid(row=f_row_index, column=f_col_index, padx=23, pady=0, sticky='ew')
                
                if self.uniform:
                    self.widget.grid_columnconfigure(f_col_index, weight=1, uniform=f"Grid {self.label}")

                f_col_index += 1

            #self.widget.grid_rowconfigure(f_row_index, weight=1, uniform=f"{self.label}")
            f_row_index += 1

@dataclass
class DClick(D):
    offset: int
    size: int = 1
    val_on: int = 1
    val_off: int = 0
    text: str = ''
    bind: None = None
    var: None = None
    widget: None = None

    def create(self, parent, **kwargs):
        self.var = tk.BooleanVar()
        self.widget = ttk.Checkbutton(
            parent,
            variable=self.var,
            text=self.text,
            command=self.click,
            style="TCheckbutton",
            **kwargs
        )

    def read_value(self):
        if self.bind is None:
            self.bind = DEntry(0x0)
            self.bind.var = tk.IntVar()
        value = savedata.get_value(self.offset, self.size)
        self.bind.var.set(value)
        if value == self.val_on: 
            self.var.set(True)
            if self.bind.var is not None and self.bind.widget is not None:
                self.bind.widget.configure(state="disabled")
        else:
            self.var.set(False)

    def write_value(self):
        value = int(self.bind.var.get())
        savedata.set_value(value, self.offset, self.size)

    def click(self):
        value = bool(self.var.get())
        if value:
            self.bind.var.set(self.val_on)
            if self.bind.widget is not None:
                self.bind.widget.configure(state="disabled")
        else:
            self.bind.var.set(self.val_off)
            if self.bind.widget is not None:
                self.bind.widget.configure(state="enabled")

def make_descr_invenventory(start_offset):
    frame_content = [[DLabel(label) for label in ('', 'Item', 'Qty', '', 'Max', '', 'Dmg', 'Rld', 'Cap','Crt', 'Prc', 'Rng','Zom', 'I', 'R')]]
    offset = start_offset
    for i in range(10):
        row = [
            DLabel(f'{i+1}'),
            DCombobox(offset, 2, options=dict_weapons, width=25),
            DEntry(offset+4, 4, width=5),
            DLabel('/'),
            DEntry(offset+8, 4, width=5),
            DLabel('', width=2)]
        [row.append(DEntry(off, 1, width=4)) for off in (offset+28, offset+30, offset+31, offset+33, offset+34, offset+35, offset+36)]
        row.append(DClick(offset+31, 1, val_on=127, val_off=0, bind=row[8]))
        row.append(DClick(offset+29, 1, val_on=102, val_off=0))
        frame_content.append(row)
        offset += 0x2C
    return frame_content

def make_descr_treasures(column_size):
    frame_content = list()
    for i in range(column_size):
        frame_content.append(list())
    offset = 0x3ad4
    for i in range(50):
        row_no = i % column_size
        frame_content[row_no].append(DLabel(str(i+1), width=2))
        frame_content[row_no].append(DCombobox(offset, 2, options=dict_treasure, width=25))
        frame_content[row_no].append(DEntry(offset+2, 1, width=3))
        frame_content[row_no].append(DLabel('', width=2))
        offset += 0x4
    labels = list()
    for i in range(50 // column_size):
        for item in (None, DLabel('Item'), DLabel('Qty'), None):
            labels.append(item)
    frame_content.insert(0, labels)
    return frame_content

def make_descr_checkarray(offset, labels_list, rows):
    checkarray = list()
    row_no = 0
    no = 0
    for item in labels_list:
        if len(checkarray) <= row_no:
            checkarray.append(list())
        if item == '#separator':
            checkarray[row_no].append(DSeparator())
        else:
            checkarray[row_no].append(DCheckbutton(offset, no, item))
            no += 1
        row_no += 1
        if row_no >= rows:
            row_no = 0
    return checkarray

def make_descr_levels():
    labels = ('', '1–1', '1–2', '2–1', '2–2', '2–3', '3–1', '3–2', '3–3', '4–1', '4–2', '5–1', '5–2', '5–3', '6–1', '6–2', '6–3')
    frame_content = [
        [DLabel(label) for label in labels],
        [DLabel('Amateur')],
        [DLabel('Normal')],
        [DLabel('Veteran')],
        [DLabel('Professional')]]
    for i in range(16):
        for j in range(1,5):
            frame_content[j].append(DCheckbutton(0x1bc + (0x4 * (j-1)), i))
    return frame_content

savedata = RE5SaveData()

list_cutscenes = ["No.01 Welcome to Africa", "No.02 Magic Act", "No.03 The Butcher (Part 1)", "No.04 The Butcher (Part 2)", "No.05 First Encounter", "No.06 Hospitality", "No.07 Guardian Angel", "No.08 A Cry for Help", "No.09 Damsel in Distress", "No.10 A Piece of the Puzzle", "No.11 Unidentified Threat", "No.12 The Storage Facility", "No.13 The Chainsaw Majini", "No.14 To the Crash Site!", "No.15 Rendezvous", "No.16 Irving's Great Escape", "No.17 Terror from Above", "No.18 Roll Out!", "No.19 Shaking Off the Majini", "No.20 Grand Resurgence", "No.21 Delta Team's Distress", "No.22 The Wetlands", "No.23 Shadows of the Past", "No.24 Josh to the Rescue", "No.25 Splitting Up", "No.26 Irving's Web", "No.27 The Oil Field Aflame", "No.28 Boat Majini Appear", "No.29 The Patrol Boat", "No.30 A New Clue", "No.31 The Docks", "No.32 The Bridge Collapses", "No.33 Wesker's Return", "No.34 Underground Garden", "No.35 Experimental Facility", "No.36 U-8 Attacks", "No.37 U-8 Repelled", "No.38 Monitored Communications", "No.39 Uroboros", "No.40 Two on Two", "No.41 Old Friends, New Enemies", "No.42 Favor for a Friend", "No.43 The Tanker", "No.44 Medicine", "No.45 Dreams of a Madman", "No.46 A New Nightmare Begins", "No.47 A Message from Jill", "No.48 Rematch", "No.49 Wesker's Vulnerability", "No.50 Sky-high Skirmish", "No.51 The Final Curtain", "No.52 The Fall of Wesker", "No.53 Homeward Bound!"]
list_infammo = ["M92F", "H&K P8", "SIG P226", "M93R", "Ithaca M37", "M3", "Jail Breaker", "Hydra", "VZ61", "AK-74", "H&K MP5", "SIG 556", "S75", "Dragunov SVD", "H&K PSG-1", "S&W M29", "Lightning Hawk", "S&W M500", "Rocket launcher"]
list_figures = ["No.01 Chris (BSAA)", "No.02 Sheva (BSAA)", "No.03 Josh", "No.04 Jill (Brainwashed)", "No.05 Wesker", "No.06 Excella", "No.07 Irving", "No.08 Spencer", "No.09 DeChant", "No.10 Dave", "No.11 Kirk", "No.12 Reynard", "No.13 Majini (Town A)", "No.14 Majini (Town B)", "No.15 Majini (Town C)", "No.16 Majini (Town D)", "No.17 Majini (Cephalo)", "No.18 Majini (Agitator)", "No.19 Majini (Wetlands A)", "No.20 Majini (Wetlands B)", "No.21 Majini (Wetlands C)", "No.22 Giant Majini", "No.23 Majini (Base A)", "No.24 Majini (Base B)", "No.25 Majini (Duvalia)", "No.26 Reaper", "No.27 Big Man Majini", "No.28 Executioner Majini", "No.29 Chainsaw Majini", "No.30 Gatling gun Majini", "No.31 Motorcycle Majini", "No.32 Uroboros", "No.33 Licker", "No.34 Kipepeo", "No.35 Bui Kichwa", "No.36 Adjule", "No.37 Crocodile", "No.38 Uroboros Aheri", "No.39 U-8", "No.40 Popokarimu", "No.41 Ndesu", "No.42 Irving (Transformed)", "No.43 Chris (Rare)", "No.44 Sheva (Rare)", "No.45 Jill (Rare)", "No.46 Wesker (Rare)"]
list_files = ["No.01 History of RESIDENT EVIL", "No.02 BSAA", "No.03 Majini", "No.04 Chris Redfield", "No.05 Sheva Alomar", "No.06 Ricardo Irving", "No.07 Ndipaya Tribe", "No.08 U-8", "No.09 Tricell", "No.10 Jill Valentine", "No.11 Excella Gionne", "No.12 Albert Wesker"]
list_shop = ['M92F (HG)', 'H&K P8 (HG)', 'SIG P226 (HG)', 'M93R (HG)', 'Ithaca M37 (SG)', 'M3 (SG)', 'Jail Breaker (SG)', 'Hydra (SG)', 'VZ61 (MG)', 'AK-74 (MG)', 'H&K MP5 (MG)', 'SIG 556 (MG)', 'S75 (RIF)', 'Dragunov SVD (RIF)', 'H&K PSG-1 (RIF)', 'S&W M29 (MAG)', 'Lightning Hawk (MAG)', 'S&W M500 (MAG)', 'Grenade launcher', 'Rocket launcher', 'Stun rod', 'Gatling gun', 'Longbow', 'Proximity bomb', 'Explosive rounds', 'Acid rounds', 'Nitrogen rounds', 'Flame rounds', 'Flash rounds', 'Electric rounds', 'First aid spray', 'Melee vest', 'Bulletproof vest']
list_bonus = ['Chris Outfit (Safari)', 'Sheva Outfit (Clubbin\')', 'Chris Outfit (S.T.A.R.S.)', 'Sheva Outfit (Tribal)', '#separator', 'Filter (Classic Horror)', 'Filter (Retro)', 'Filter (Noise)', '#separator', 'Chris (BSAA) ', 'Sheva (BSAA) ', 'Josh  ', 'Jill (Brainwashed) ', 'Wesker  ', 'Excella  ', 'Irving  ', 'Spencer  ', 'DeChant  ', 'Dave  ', 'Kirk  ', 'Reynard  ', 'Majini (Town A)', 'Majini (Town B)', 'Majini (Town C)', 'Majini (Town D)', 'Majini (Cephalo) ', 'Majini (Agitator) ', 'Majini (Wetlands A)', 'Majini (Wetlands B)', 'Majini (Wetlands C)', 'Giant Majini ', 'Majini (Base A)', 'Majini (Base B)', 'Majini (Duvalia) ', 'Reaper  ', 'Big Man Majini', 'Executioner Majini ', 'Chainsaw Majini ', 'Gatling gun Majini', 'Motorcycle Majini ', 'Uroboros  ', 'Licker  ', 'Kipepeo  ', 'Bui Kichwa ', 'Adjule  ', 'Crocodile  ', 'Uroboros Aheri ', 'U-8  ', 'Popokarimu  ', 'Ndesu  ', 'Irving (Transformed) ', 'Chris (Rare) ', 'Sheva (Rare) ', 'Jill (Rare) ', 'Wesker (Rare) ']
list_characters = ['A / Chris Redfield (Safari)', 'B / Chris Redfield (S.T.A.R.S.)', 'C / Sheva Alomar (Clubbin\')', 'D / Sheva Alomar (Tribal)', 'E / Jill Valentine (BSAA)', 'F / Jill Valentine (Battle suit)', 'G / Albert Wesker (Midnight)', 'H / Albert Wesker (S.T.A.R.S.)']
dict_filter = {'Default': 0x0, 'Classic Horror': 0x1, 'Retro': 0x2, 'Noise': 0x3}
dict_chriscostume = {'BSAA': 0x0, 'Safari': 0x1, 'S.T.A.R.S.': 0x2, 'Warrior': 0x300000000, 'Heavy Metal': 0x400000000, 'Plain': 0x900000000, 'Lost in Nightmares': 0xD00000000} # Extra 0xa - stars, 0xb - safari, 0xc - warrior
dict_shevacostume = {'BSAA': 0x0, 'Clubbin\'': 0x1, 'Tribal': 0x2, 'Business': 0x300000000, 'Fairy Tale': 0x400000000}
dict_weapons = {'None': 0, 'M92F (HG)': 258, 'H&K P8 (HG)': 272, 'SIG P226 (HG)': 273, 'M93R (HG)': 286, 'Px4 (HG)': 287, 'Samurai Edge (Wesker) (HG)': 297, 'Samurai Edge (Barry) (HG)': 274, 'Ithaca M37 (SG)': 260, 'M3 (SG)': 278, 'Jail Breaker (SG)': 279, 'Hydra (SG)': 281, 'VZ61 (MG)': 259, 'AK-74 (MG)': 285, 'H&K MP5 (MG)': 275, 'SIG 556 (MG)': 265, 'S75 (RIF)': 261, 'Dragunov SVD (RIF)': 288, 'H&K PSG-1 (RIF)': 284, 'S&W M29 (MAG)': 267, 'Lightning Hawk (MAG)': 282, 'S&W M500 (MAG)': 283, 'Grenade launcher (EXP)': 293, 'Grenade launcher (ACD)': 294, 'Grenade launcher (ICE)': 295, 'Grenade launcher (FLM)': 313, 'Grenade launcher (FLS)': 314, 'Grenade launcher (ELC)': 315, 'Grenade launcher (INV)': 268, 'Rocket launcher': 269, 'Rocket launcher (Inf.)': 312, 'Stun rod': 290, 'Gatling gun': 277, 'Longbow': 271, 'Flamethrower': 289, 'L.T.D.': 308, 'RPG-7 NVS': 309, 'Knife (Chris)': 257, 'Knife (Sheva)': 270, 'Knife (Josh)': 276, 'Knife (Wesker)': 291, 'Knife (Jill)': 292, 'Hand-to-hand': 311, 'Hand grenade': 262, 'Incendiary grenade': 263, 'Flash grenade': 264, 'Proximity bomb': 266, 'Egg (White)': 316, 'Egg (Brown)': 317, 'Egg (Golden)': 318, 'Egg (Rotten)': 310, 'Handgun ammo': 513, 'Machine gun ammo': 514, 'Shotgun sells': 515, 'Riffle ammo': 516, 'Magnum ammo': 521, 'Explosive rounds': 518, 'Acid rounds': 519, 'Nitrogen rounds': 520, 'Flame rounds': 526, 'Flash rounds': 527, 'Electric rounds': 528, 'RPG round': 529, 'First aid spray': 772, 'Herb (Green)': 773, 'Herb (Red)': 774, 'Herb (G+G)': 775, 'Herb (G+R)': 777, 'Melee vest': 1537, 'Bulletproof vest': 1542}
dict_treasure = {'None': 0x0, 'Gold ring': 0x417, 'Ivory relief': 0x420, 'Dead bride\'s necklace': 0x418, 'Royal necklace': 0x423, 'Jewel bangle': 0x424, 'Venom fang': 0x419, 'Antique clock': 0x41a, 'Chalice (Silver)': 0x41b, 'Chalice (Gold)': 0x41c, 'Idol (Silver)': 0x41d, 'Idol (Gold)': 0x41e, 'Ceremonial mask': 0x41f, 'Jewel beetle': 0x422, 'Beetle (Brown)': 0x421, 'Beetle (Gold)': 0x425, 'Topaz (Pear)': 0x450, 'Ruby (Pear)': 0x451, 'Sapphire (Pear)': 0x452, 'Emerald (Pear)': 0x453, 'Diamond (Pear)': 0x454, 'Topaz (Square)': 0x457, 'Ruby (Square)': 0x458, 'Sapphire (Square)': 0x459, 'Emerald (Square)': 0x45a, 'Diamond (Square)': 0x45b, 'Topaz (Oval)': 0x45e, 'Ruby (Oval)': 0x45f, 'Sapphire (Oval)': 0x460, 'Emerald (Oval)': 0x461, 'Diamond (Oval)': 0x462, 'Topaz (Trilliant)': 0x465, 'Ruby (Trilliant)': 0x466, 'Sapphire (Trilliant)': 0x467, 'Emerald (Trilliant)': 0x468, 'Diamond (Trilliant)': 0x469, 'Topaz (Brilliant)': 0x47a, 'Ruby (Brilliant)': 0x47b, 'Sapphire (Brilliant)': 0x47c, 'Emerald (Brilliant)': 0x47d, 'Diamond (Brilliant)': 0x47e, 'Topaz (Marquise)': 0x473, 'Ruby (Marquise)': 0x474, 'Sapphire (Marquise)': 0x475, 'Emerald (Marquise)': 0x476, 'Diamond (Marquise)': 0x477, 'Power stone': 0x46c, 'Lion heart': 0x46d, 'Blue enigma': 0x46e, 'Soul gem': 0x46f, 'Heart of Africa': 0x470}
dict_difficulty = {'Amateur': 0, 'Normal': 1, 'Veteran': 2, 'Professional': 3}
dict_chapter = {'1–1': 0, '1–2': 1, '2–1': 2, '2–2': 3, '2–3': 4, '3–1': 5, '3–2': 6, '3–3': 7, '4–1': 8, '4–2': 9, '5–1': 10, '5–2': 11, '5–3': 12, '6–1': 13, '6–2': 14, '6–3': 15, '6–4': 16}
dict_area = {'1–1 Civilian Checkpoint': 0x06400000000, '1–1 Back alley': 0x07300000000, '1–1 Public Assembly': 0x07200000000, '1–2 Public Assembly': 0x07200000001, '1–2 Urban District': 0x06600000001, '1–2 Abandoned Building': 0x07500000001, '1–2 Furnace Facility': 0x06700000001, '2–1 Storage Facility': 0x07600000002, '2–1 The Bridge': 0x06800000002, '2–1 The Port': 0x07100000002, '2–1 Shanty Town': 0x06900000002, '2–1 Train Yard': 0x06a00000002, '2–2 Train Station': 0x07700000003, '2–2 The Mines': 0x06b00000003, '2–2 Mining Area': 0x06c00000003, '2–3 Savannah': 0x06d00000004, '2–3 The Port (Night)': 0x06f00000004, '3–1 Marshlands': 0x25e00000005, '3–1 m2': 0x0c800000005, '3–1 Village': 0x0ca00000005, '3–2 Execution Grounds': 0x0c900000006, '3–2 Oil Field - Refinery': 0x0cf00000006, '3–2 Oil Field - Control Facility': 0x0cb00000006, '3–2 Oil Field - Dock': 0x0d100000006, '3–3 Oil Field - Drilling Facilities': 0x0cc00000007, '3–3 Patrol Boat': 0x0cd00000007, '4–1 Caves': 0x13900000008, '4–1 Ancient Village': 0x12c00000008, '4–1 Labyrinth': 0x12d00000008, '4–2 Worship Area': 0x12e00000009, '4–2 Pyramid': 0x12f00000009, '4–2 Underground Garden': 0x13800000009, '5–1 Underground Garden': 0x1380000000A, '5–1 Progenitor Virus House': 0x1310000000A, '5–1 Experimental Facility': 0x1300000000A, '5–2 Experimental Facility': 0x1300000000B, '5–2 Power Station': 0x1360000000B, '5–2 Experimental Facility Passage': 0x13c0000000B, '5–2 Missile Area 1st Floor': 0x1330000000B, '5–2 Uroboros Research Facility': 0x1340000000B, '5–3 Uroboros Research Facility': 0x1340000000C, '5–3 Missile Area 2nd Floor': 0x13a0000000C, '5–3 Moving Platform': 0x13b0000000C, '5–3 Monarch Room': 0x1350000000C, '6–1 Ship Deck': 0x1f40000000D, '6–1 Ship Hold': 0x1f50000000D, '6–2 Main Deck': 0x1f70000000E, '6–2 Bridge': 0x1f80000000E, '6–2 Bridge Deck': 0x1ff0000000E, '6–3 Bridge Deck': 0x1ff0000000F, '6–3 Bridge': 0x2000000000F, '6–3 Engine Room': 0x1f90000000F, '6–3 Hangar': 0x1fa0000000F, '6–3 Volcano': 0x1fc0000000F, '6–4 Credits': 0x26300000010}

tabs = {
    'Progression': [
        [DTabFrame('Last save', uniform=False),  DTabFrame('General', uniform=False),            DTabFrame('Current', uniform=False),  DTabFrame('Characters', uniform=False)],
        [DTabFrame('Warning'),                   DTabFrame('Levels', colspan=2, uniform=False),  None,                                 DTabFrame('Versus', uniform=False)]
    ],
    'Inventory': [
        [DTabFrame('Chris', uniform=False),      DTabFrame('Sheva', uniform=False)]
    ],
    'Treasure': [
        [DTabFrame('Treasure', uniform=False)]
    ],
    'Special': [
        [DTabFrame('Special Settings', colspan=2, uniform=False),   None, DTabFrame('Filters'),  DTabFrame('Infinite Ammo', rowspan=2),  DTabFrame('Versus Characters', rowspan=2)],
        [DTabFrame('Chris Outfits'),                                DTabFrame('Sheva Outfits')]
    ],
    'Unlocks': [
        [DTabFrame('Shop'),     DTabFrame('Bonus Features')]
    ],
    'Library': [
        [DTabFrame('Files'),    DTabFrame('Figures')]
    ],
    'Library cont.': [
        [DTabFrame('Cutscenes')]
    ]
}

frames = {
    'Warning':[
        [DLabel('')],
        [DLabel('This code is designed to work exclusively \nwith save files from the Steam release of \nResident Evil 5 Gold Edition (version 1.2.0).')],
        [DLabel('')],
        [DLabel('Always make backups!')]
    ],
    'Last save': [
        [DLabel('')],
        [DLabel('YYYY-MM-DD'),  DEntry(0x10, 4, max=2099, width=4),  DLabel('-'),  DEntry(0x14, 4, max=12, width=4),  DLabel('-'),  DEntry(0x18, 4, max=12, width=4)],
        [DLabel('HH:MM:SS'),    DEntry(0x1c, 4, max=23, width=4),    DLabel(':'),  DEntry(0x20, 4, max=59, width=4),  DLabel(':'),  DEntry(0x24, 4, max=59, width=4)],
    ],
    'Versus': [
        [None,                      DLabel('Played'),            DLabel('Won')],
        [DLabel('Slayers'),         DEntry(0x0C98, 4, width=5),  DEntry(0x0C9C, 4, width=5),   DLabel('Melee kills'), DEntry(0x182, 2, width=5)],
        [DLabel('Survivors'),       DEntry(0x12D8, 4, width=5),  DEntry(0x12DC, 4, width=5)],
        [DLabel('Team Slayers'),    DEntry(0x1990, 4, width=5),  DEntry(0x1994, 4, width=5)],
        [DLabel('Team Survivors'),  DEntry(0x1FD0, 4, width=5),  DEntry(0x1FD4, 4, width=5)],
    ],
    'General': [
        [DLabel('SteamID'),          DEntry(0x0, 4)],
        [DLabel('Playtime, sec'),    DEntry(0x18c, 4)],
        [DLabel('Money'),            DEntry(0x194, 4, max=9999999)],
        [DLabel('Exchange Points'),  DEntry(0x198, 4, max=9999999)],
    ],
    'Characters': [
        [None,             DLabel('HP'),                None,         DLabel('Max'), None, DLabel('Exists')],
        [DLabel('Chris'),  DEntry(0x3C50, 4, width=5),  DLabel('/'),  DEntry(0x3c54, 4, width=5), DLabel('', width=2), DCheckbutton(0x3C40)],
        [DLabel('Sheva'),  DEntry(0x3CA0, 4, width=5),  DLabel('/'),  DEntry(0x3CA4, 4, width=5), DLabel('', width=2), DCheckbutton(0x3C90)],
    ],
    'Current': [
        [DLabel('State'),            DCombobox(0x3bb0, 4, {'New Game': 0, 'Continue': 1, 'New Game +': 2}, width=30)],
        [DLabel('Character'),        DCombobox(0x3bb4, 1, options={'Chris Redfield': 0x0, 'Sheva Alomar': 0x1}, width=30)],
        [DLabel('Difficulty'),       DCombobox(0x3bb8, 4, dict_difficulty, width=30)],
        [DLabel('Area'),             DCombobox([0x3bc0, 0x3bc8], 4, dict_area, width=30)],
        #[DLabel('Co-op settings'),   DCombobox(0x60, 4, {'No Limits': 0, 'Invite Only': 1, 'Rogue': 2})],
        #[DLabel('Attack reaction'),  DCheckbutton(0x64, text='Enabled')],        
    ],
    'Special Settings': [
        [DLabel('Chris costume'),       DCombobox([0x50, 0x5d44], 4, dict_chriscostume)],
        [DLabel('Sheva costume'),       DCombobox([0x54, 0x5d48], 4, dict_shevacostume)],
        [DLabel('Filter'),              DCombobox(0x58, 4, dict_filter)],
        [DLabel('Infinite Ammo Mode'),  DCheckbutton(0x5C, 0)],
    ],
    'Chris Outfits':     make_descr_checkarray(0x124, ['BSAA', 'Safari', 'S.T.A.R.S.', 'Warrior', 'Heavy Metal'], 12),
    'Sheva Outfits':     make_descr_checkarray(0x128, ['BSAA', 'Clubbin\'', 'Tribal', 'Business', 'Fairy Tale'], 12),
    'Filters':           make_descr_checkarray(0x12c, ['Default', 'Classic Horror', 'Retro', 'Noise'], 12),
    'Infinite Ammo':     make_descr_checkarray(0x130, list_infammo, 11),
    'Files':             make_descr_checkarray(0x134, list_files, 12),
    'Figures':           make_descr_checkarray(0x138, list_figures, 12),
    'Cutscenes':         make_descr_checkarray(0x140, list_cutscenes, 12),
    'Shop':              make_descr_checkarray(0x148, list_shop, 12),
    'Bonus Features':    make_descr_checkarray(0x158, list_bonus, 12),
    'Versus Characters': make_descr_checkarray(0x180, list_characters, 11),
    'Levels':            make_descr_levels(),
    'Treasure':          make_descr_treasures(10),
    'Chris':             make_descr_invenventory(0x3d80),
    'Sheva':             make_descr_invenventory(0x41a0)
}

def open():
    def wrongfile():
        savedata.data = None
        messagebox.showerror("Not a Save File", "The file you are trying to open cannot be processed because it contains unexpected data or does not match the expected structure — i.e., it is not a Resident Evil 5 (PC) save file.")

    filepath = filedialog.askopenfilename(
        title="Open Savegame",
        filetypes=(("Savegame", "*.bin"), ("All Files", "*.*"))
    )
    if filepath:
        size = os.path.getsize(filepath)
        if size < 23800 or size > 24000:
            wrongfile()
            return None
        savedata.open_file(filepath)
        offsets = 0x3c00, 0x3c18, 0x3c30
        value = savedata.get_value(0x3be8, 8)
        for offset in offsets:
            if value != savedata.get_value(offset, 8):
                wrongfile()
                return None
        for fframe in frames.values():
            for row in fframe:
                for cell in row:
                    
                    if type(cell) in (DLabel, DCheckbutton, DEntry, DCombobox, DClick):
                        cell.widget.configure(state="normal")
                        cell.read_value()
                    
        save_button.configure(state="normal")

def save():
    filepath = filedialog.asksaveasfilename(
        title="Save Savegame",
        defaultextension=".bin",
        filetypes=(("Savegame", "*.bin"), ("All Files", "*.*"))
    )
    if filepath:
        for fframe in frames.values():
            for row in fframe:
                for cell in row:
                    
                    if type(cell) in (DCheckbutton, DEntry, DCombobox, DClick):
                        cell.write_value()

        savedata.save_file(filepath)

def on_configure(event):
    if event.widget == root:
        sleep(0.01) # Jittery is better then slow

# Main window setup
root = tk.Tk()
root.title("ReSaveHazard")
root.resizable(False, False)
root.bind("<Configure>", on_configure)

# Icon
pypath = os.path.dirname(os.path.abspath(__file__))
icopath = os.path.join(pypath, 'icon.ico')
root.iconbitmap(default=icopath)

# Style
themepath = os.path.join(pypath, 'forest-dark.tcl')
try:
    root.tk.call('source', themepath)
    ttk.Style().theme_use('forest-dark')
except:
    pass

# Credits
credits_text = 'picoleet: file reverse engineering\nBiohazard4X: offsets and ideas'
credits_text2 ='rdbende: Forest-ttk-theme\nzoom4h: menus and errors'

# Button frame setup
button_frame = ttk.Frame(root)
button_frame.pack(fill='both', expand=True, padx=10, pady=5)

open_button = ttk.Button(button_frame, text="Open", style='Accent.TButton', command=open)
save_button = ttk.Button(button_frame, text="Save", style='Accent.TButton', command=save, state="disabled")

empty = ttk.Label(button_frame, text='')

credits = ttk.Label(button_frame, text=credits_text)
credits2 = ttk.Label(button_frame, text=credits_text2)

elements = open_button, save_button, empty, credits, credits2
for i in (range(5)):
    elements[i].grid(row=0, column=i, sticky='nesw', padx=40, pady=5)
    button_frame.grid_columnconfigure(i, weight=1, uniform='main')

# Notebook setup
notebook = ttk.Notebook(root)
notebook.pack()

for tab_name, tab_content in tabs.items():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_name)
    row_index = 0
    for row in tab_content:

        col_index = 0
        for frame in row:
            
            if type(frame) is DTabFrame:
                frame.create(tab, row_index, col_index)

            tab.grid_columnconfigure(col_index, weight=1)
            col_index += 1

        tab.grid_rowconfigure(row_index, weight=1) 
        row_index += 1

# Run
root.mainloop()