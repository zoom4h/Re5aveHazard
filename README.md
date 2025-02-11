# Re5aveHazard

![image](https://github.com/zoom4h/Re5aveHazard/blob/screenshots/scr1.png?raw=true)
![image](https://github.com/zoom4h/Re5aveHazard/blob/screenshots/scr2.png?raw=true)
![image](https://github.com/zoom4h/Re5aveHazard/blob/screenshots/scr3.png?raw=true)

This Python program allows for the modification of *Resident Evil 5 v1.2.0* (Steam release) save files. It supports editing a variety of in-game values, including:

- **SteamID**
- **Money (Pts)**
- **Level progress**
- **Bonus features**
- **Costumes** (including two normally unavailable ones)
- **Weapons** (including some normally unavailable ones)

The program operates directly on the save file, ensuring no memory injection or game file corruption occurs.

---

## How to Run

### Prebuilt Windows `.exe`
1. Download the [latest release](https://github.com/zoom4h/Re5aveHazard/releases/latest).
2. Launch `Re5aveHazard.exe`.  
   *Note: Antivirus software may flag the executable since it is unsigned.*

---

### Run from Source (`.py`) with Python
1. Install [Python 3.11.7](https://www.python.org/downloads/) or a compatible version.
2. Download the [source code from this repository](https://github.com/zoom4h/Re5aveHazard/archive/refs/heads/main.zip).
3. Unpack the files to a directory of your choice.
4. Run the program with:
   ```bash
   python gui.py
   ```

   **Optional:** For improved visuals, download the [Forest-ttk-theme](https://github.com/rdbende/Forest-ttk-theme) and place the `forest-dark` folder and `forest-dark.tcl` file in the same directory as `gui.py`.

---

### Build `.exe` Yourself
1. Install [Python ≥ 3.11.7](https://www.python.org/downloads/).
2. Install Nuitka:
   ```bash
   python -m pip install nuitka
   ```
3. Download the [source code from this repository](https://github.com/zoom4h/Re5aveHazard/archive/refs/heads/main.zip) and unpack it into your build directory.
4. Optionally, download the [Forest-ttk-theme](https://github.com/rdbende/Forest-ttk-theme) and place the `forest-dark` folder and `forest-dark.tcl` file in the build directory.
5. Open a command prompt in the build directory and run:
   ```bash
   python -m nuitka gui.py --output-filename=Re5aveHazard --standalone --onefile --windows-console-mode=disable --windows-icon-from-ico=icon.ico --enable-plugin=tk-inter --include-data-files=forest-dark.tcl=forest-dark.tcl --include-data-files=icon.ico=icon.ico --include-data-dir=forest-dark=forest-dark
   ```
