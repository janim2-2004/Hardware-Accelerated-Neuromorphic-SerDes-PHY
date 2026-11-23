# Alchitry Au V2 Onboarding Guide

Nov 22, 2026 · @Raymond

## Overview

This guide takes you from a blank Windows PC to a working Alchitry Au V2 board you can program from both Alchitry Labs and Vivado. Plan for about 2–3 hours, most of it waiting for the Vivado download and install.

By the end you will have:

1. Vivado (the AMD tool that turns Verilog into a bitstream) and Alchitry Labs V2 (Alchitry's simpler editor and loader) installed.
2. Confirmed the board works by blinking its LEDs from an Alchitry Labs project.
3. Built and loaded the same test from your own Vivado project in Verilog. This is the setup used for the capstone RTL.

Every step was tested on Windows with Vivado 2025.2 and Alchitry Labs 2.0.63. Menu names can move slightly between versions; if a button is not where this guide says, look for the same name nearby.

## What you need

| Item | Details |
| --- | --- |
| Board | Alchitry Au V2 (Artix-7, part `xc7a35tftg256-2`). Not the older Au V1, which has different pins. |
| USB-C cable | Must be a **data** cable. Charge-only cables power the board but the PC never sees it. |
| PC | Windows or Linux, 64-bit. Vivado does not run on macOS. |
| Disk space | Plan for roughly 40–80 GB free for Vivado. Selecting only Artix-7 keeps it at the low end. |
| AMD account | Free. Needed to download and install Vivado. Sign up at amd.com. |
| Internet | The Vivado web installer downloads several GB during install. |

Use folder paths with **no spaces** for all projects (for example `C:\School\Capstone\...`). Vivado sometimes fails on paths with spaces.

## Part 1: Install Vivado

Vivado is AMD's free tool that builds your design into a bitstream and programs the board. Install it first, since Alchitry Labs uses it in the background.

1. Go to the AMD website and open the **Downloads** page for Vivado (search "Vivado download"). Pick the latest version and download the **web installer** for your OS (Windows `.exe` or Linux `.bin`). The web installer is the only option since 2024.1.
2. Run the installer.
   - Windows: double-click the `.exe`.
   - Linux: run `chmod +x <file>.bin`, then `./<file>.bin`.
3. **Sign in** with your AMD account on the first screen, then click **Next**.
4. **Accept** all the license agreements (tick each box at the bottom of the page), then **Next**.
5. **Select Product:** choose **Vivado**, then **Next**.
6. **Select Edition:** choose **Vivado ML Standard**. This is the free edition and it supports the Au V2's chip. Then **Next**.
7. **Customize installation** (the page with a tree of checkboxes):
   - Under **Devices → 7 Series**, tick **Artix-7**. Untick other device families you don't need to save space.
   - On Windows, leave **Install Cable Drivers** ticked (near the bottom of the list). Without it, Vivado's Hardware Manager cannot see the board.
8. **Select destination directory:** keep the default (for example `C:\AMDDesignTools`) or pick another folder with no spaces. **Write this path down**; you need it in Part 2.
9. Click **Install** on the summary page and wait. It can take an hour or more.
10. When it finishes, Vivado appears in the Start menu. You don't need to open it yet.

**Find the Vivado folder for later.** Open File Explorer in your install folder and go down until you reach a folder named `Vivado` with a `bin` folder directly inside it, for example `C:\AMDDesignTools\2025.2\Vivado`. That exact folder is the "Vivado location". Tip: right-click the Vivado Start-menu shortcut → **Open file location** to jump close to it.

## Part 2: Install Alchitry Labs and connect it to Vivado

Alchitry Labs V2 is a small editor that sends your project to Vivado for building and then loads the result onto the board. It is the quickest way to check that a board and PC work.

1. Go to **alchitry.com → Alchitry Labs** and download the **Alchitry Labs V2** installer for your OS. Run it. If Windows Defender warns about an unknown app, click **More info → Run anyway**.
2. Open Alchitry Labs. If it offers an update on first launch, accept it.
3. Open the **Settings** menu in the menu bar at the top of the window and choose the **Vivado location** option.
4. Select the `Vivado` folder you found at the end of Part 1 (the one with `bin` directly inside it).

| Choose this | Not these |
| --- | --- |
| `C:\AMDDesignTools\2025.2\Vivado` | `C:\AMDDesignTools` (too high), `C:\AMDDesignTools\2025.2` (too high), `...\Vivado\bin` (too deep), the desktop shortcut |

No extra USB drivers are needed for Alchitry Labs. Plug the board in now so it is ready for Part 3.

## Part 3: Program the board with Alchitry Labs

This test makes the 8 LEDs count in binary. If it works, your Vivado install, USB cable and board are all good.

### Create the project

1. In Alchitry Labs, choose **New Project** (from the start screen, or the menu at the top left).
2. Fill in:
   - **Name:** `au_bringup`
   - **Location:** a folder with no spaces
   - **Board:** **Alchitry Au V2** (not plain "Au")
   - **Template:** **Base Project**
3. Click **Create**. There is no language option: Alchitry Labs V2 projects use Lucid, Alchitry's own language. That's fine for this test.

### Edit the code

4. In the file list on the left, open **`alchitry_top.luc`**.
5. Replace its contents with the code below. It adds a 27-bit counter (`dff counter[27]`, like a Verilog `reg [26:0]`) and shows its top 8 bits on the LEDs.

```
module alchitry_top (
    input clk,              // 100MHz clock
    input rst_n,            // reset button (active low)
    output led[8],          // 8 user controllable LEDs
    input usb_rx,           // USB->Serial input
    output usb_tx           // USB->Serial output
) {

    sig rst                 // reset signal

    .clk(clk) {
        reset_conditioner reset_cond

        .rst(rst) {
            dff counter[27]         // 27-bit counter
        }
    }

    always {
        reset_cond.in = ~rst_n  // input raw inverted reset signal
        rst = reset_cond.out    // conditioned reset

        counter.d = counter.q + 1   // count up every clock cycle
        led = counter.q[26:19]      // top 8 counter bits on the LEDs

        usb_tx = usb_rx         // echo the serial data
    }
}
```

6. Save with **Ctrl+S**.

### Build and load

7. Click the **hammer icon** in the toolbar at the top of the window to build. Alchitry Labs runs Vivado in the background. The first build takes a few minutes and the log may look stuck; that's normal. Wait for a green **Finished building** message in the log panel.
8. Make sure the board is plugged in, then load it using one of the two load (arrow) buttons next to the hammer:
   - **Solid down-arrow = load to flash.** The design stays after you unplug the board. Use this for the test.
   - **Hollow arrow = load to RAM.** Faster, but lost when power is removed.

### Check it works

| Test | Expected result |
| --- | --- |
| Load finishes with no error | The PC sees the board |
| LEDs count in binary; `led[7]` toggles about every 0.67 s | Clock, LED pins and your code all work |
| Hold the reset button | LEDs go dark; counting restarts from 0 when released |
| Unplug and replug the board | Blinking resumes on its own (flash works) |
| Change `[26:19]` to `[25:18]`, build, load | Everything blinks twice as fast |

If a build fails, scroll up in the log to the **first** red `ERROR:` line; later errors are usually caused by it. See Troubleshooting at the end.

## Part 4: Program the board with Vivado

The capstone RTL is written in Verilog in a normal Vivado project, because it needs Vivado features like the Clocking Wizard and the ILA (on-chip logic analyzer). This part builds the same LED counter that way.

**Where things are in the Vivado window:**

| Area | Location | Used for |
| --- | --- | --- |
| Flow Navigator | Panel down the **left side** | Settings, Add Sources, Generate Bitstream, Hardware Manager |
| Sources | Panel at the **top middle** (tab) | Your design and constraint files |
| Editor | **Right/centre**, opens when you double-click a file | Editing code |
| Tcl Console, Messages, Design Runs | Tabs along the **bottom** | Typing commands, errors/warnings, build status |

### Step 1: Set up a folder

```
tx_fpga/
├─ rtl/        your Verilog files
├─ constr/     your .xdc constraints file
└─ vivado/     the Vivado project (do not commit to Git)
```

The rule behind this layout: **your own files live in `rtl/` and `constr/`; everything Vivado generates lives in `vivado/`.** You can delete `vivado/` and rebuild without losing any of your work.

| Folder | What's in it | Who writes it | Commit to Git? |
| --- | --- | --- | --- |
| `rtl/` | Verilog design files: `top.v` now, later `clk_rst_gen.v`, `tx_phy.v`, `pattern_gen.v` and so on | You | Yes |
| `constr/` | Constraints file `au_v2.xdc` | You | Yes |
| `vivado/` | Vivado project file, build outputs, reports, the bitstream | Vivado | No |

#### `rtl/`: the circuit

The Verilog here describes the logic inside the FPGA. It says nothing about the board around the chip.

#### `constr/`: how the circuit connects to the board

The `.xdc` file gives Vivado the facts Verilog can't express:

- **Pin locations** (`PACKAGE_PIN`): which of the chip's 256 pins each port uses. These must match the copper traces on the board, so `clk` must be N14 because that is where the oscillator is wired.
- **Voltage standards** (`IOSTANDARD`): the voltage each pin uses, which must match how the board powers that bank of pins. This decides which pins can be used for LVDS later.
- **Clock definition** (`create_clock`): tells Vivado `clk` is 100 MHz, so it checks every path in your logic finishes within 10 ns. Clocks made by the MMCM later are worked out automatically from this one line.
- **Configuration settings**: how the board's flash chip is wired, so the design boots from flash on power-up.

Why you need it: without pin locations Vivado refuses to make a bitstream. With a wrong pin the build succeeds but the design silently doesn't work. Without the clock line Vivado can't check timing, so a design can pass on your desk and fail randomly later. Each time you add a new board connection (LVDS pairs, scope test pins), its pins go in this file.

#### `vivado/`: Vivado's workspace

Vivado creates and fills this folder. The main things in it:

| Item | What it is |
| --- | --- |
| `tx_bringup.xpr` | The project file. Double-click it to reopen the project. Stores the part number, the paths to your `rtl/` and `constr/` files, and settings like `-bin_file`. |
| `tx_bringup.runs/synth_1/` | Synthesis output: your Verilog turned into a netlist of FPGA cells, plus its log and reports. |
| `tx_bringup.runs/impl_1/` | Implementation output: placed and routed design, timing and utilization reports, and the final **`top.bit`** (and `top.bin`) you program onto the board. |
| `tx_bringup.cache/`, `.hw/`, `.ip_user_files/` | Vivado's internal cache, Hardware Manager settings, and generated IP helper files. |
| `tx_bringup.srcs/` | Where Vivado stores files it creates for you, such as IP you add from the IP Catalog. |

Why you need it: it is where Vivado keeps the project together and writes every build result, including the bitstream. Why not commit it: it is large, it changes on every build (causing Git conflicts), and it contains paths specific to your PC. A teammate makes their own by creating a project and adding the same `rtl/` and `constr/` files.

**When you add IP later** (Clocking Wizard, ILA): by default Vivado saves the IP's `.xci` file inside `vivado/`. Choose an `ip/` folder next to `rtl/` instead when you create it, and commit that, or your teammates can't rebuild your design.

If `tx_fpga` is inside the Git repo, add `tx_fpga/vivado/` to `.gitignore`.

### Step 2: Create the two source files

Save this as **`rtl/top.v`**:

```verilog
module top (
  input  wire       clk,      // 100 MHz
  input  wire       rst_n,    // reset button, active low
  output wire [7:0] led,
  input  wire       usb_rx,
  output wire       usb_tx
);
  reg [26:0] cnt;
  always @(posedge clk)
    if (!rst_n) cnt <= 27'd0;
    else        cnt <= cnt + 27'd1;

  assign led    = cnt[26:19];
  assign usb_tx = usb_rx;     // echo serial data
endmodule
```

Save the base constraints from **Board reference** (below) as **`constr/au_v2.xdc`**. Every port in `top.v` must have a pin in the `.xdc`, and the names must match exactly.

### Step 3: Create the Vivado project

1. Open Vivado. On the start page, under **Quick Start**, click **Create Project**, then **Next**.
2. **Project name:** `tx_bringup`. **Project location:** your `tx_fpga/vivado` folder. Click **Next**.
3. **Project type:** select **RTL Project** and tick **Do not specify sources at this time**. Click **Next**.
4. **Default Part:** in the **Search** box at the top, type `xc7a35tftg256-2`, click that row in the list, then **Next**.
5. Click **Finish**.

### Step 4: Add your files

1. In the Flow Navigator (left), under **PROJECT MANAGER**, click **Add Sources**.
2. Select **Add or create design sources** → **Next** → **Add Files** → choose `rtl/top.v`.
3. **Untick "Copy sources into project"** (checkbox near the bottom), then **Finish**. If it stays ticked, Vivado edits a copy and your `rtl/` file gets out of date.
4. Click **Add Sources** again → **Add or create constraints** → **Next** → **Add Files** → choose `constr/au_v2.xdc`. Untick copy again, then **Finish**.
5. In the **Sources** panel, `top` should be shown in **bold** (the top module). If not, right-click it → **Set as Top**.

### Step 5: Turn on .bin output (only needed for Alchitry Loader)

Either:

- Flow Navigator → **PROJECT MANAGER → Settings** (gear icon; also **Tools → Settings** in the top menu). In the Settings window's left list, under **Project Settings**, click **Bitstream**. In the options table on the right, tick **`-bin_file`**. Click **OK**.
- Or click the **Tcl Console** tab at the bottom, paste this and press **Enter**:

```tcl
set_property STEPS.WRITE_BITSTREAM.ARGS.BIN_FILE true [get_runs impl_1]
```

### Step 6: Build

1. In the Flow Navigator, under **PROGRAM AND DEBUG** (bottom section), click **Generate Bitstream**.
2. When asked to run synthesis and implementation first, click **Yes**, then **OK** on the launch options.
3. Wait a few minutes. Progress shows as a spinner in the **top right** corner of the window.
4. When the **Bitstream Generation Completed** pop-up appears, choose **Open Hardware Manager** and click **OK**.
5. Before programming, check two things:
   - **Messages** tab (bottom): no red errors and no critical warnings.
   - **Project Summary** (PROJECT MANAGER → Project Summary) → **Timing**: **WNS** is a positive number.

### Step 7: Program the board

1. In Hardware Manager, click **Open target** in the green bar at the top (or Flow Navigator → **Open Hardware Manager → Open Target**) → **Auto Connect**.
2. The **Hardware** panel (top left) should show `localhost` → a cable → **`xc7a35t_0`**.
3. Right-click **`xc7a35t_0`** → **Program Device**. The bitstream file box should already show `...runs/impl_1/top.bit`. Click **Program**.
4. The LEDs count. This loads into RAM: when you unplug the board, it goes back to whatever is in flash.

If Auto Connect finds nothing, use Alchitry Loader instead: in Alchitry Labs, load `vivado\tx_bringup.runs\impl_1\top.bin`. Then see Troubleshooting, because the ILA needs Hardware Manager.

### Step 8: The rebuild loop

This is the loop you will use for every change:

1. **Edit:** in the **Sources** panel, double-click `top.v` to open it (or edit `rtl/top.v` in VS Code). For a test, change `cnt[26:19]` to `cnt[25:18]`.
2. **Save:** **Ctrl+S**. The **Design Runs** tab (bottom) now shows `synth_1` and `impl_1` as **Out-of-date**.
3. **Build:** Flow Navigator → **Generate Bitstream** → **Yes**.
4. **Program:** Hardware Manager → right-click **`xc7a35t_0`** → **Program Device** → **Program**. No need to reconnect if it is still open.

The LEDs should now count twice as fast. If Vivado says the bitstream is up to date but you changed a setting, run `reset_run impl_1 -from_step write_bitstream` in the Tcl Console and build again.

## Board reference

These values come from Alchitry Labs' own generated build files for the Au V2 and were tested on the board. Vivado part string: **`xc7a35tftg256-2`**.

| Signal | Pin | Standard | Notes |
| --- | --- | --- | --- |
| `clk` | N14 | LVCMOS33 | 100 MHz oscillator |
| `rst_n` | P6 | LVCMOS33 | Reset button, active low |
| `led[0]`–`led[3]` | K13, K12, L14, L13 | LVCMOS33 |  |
| `led[4]`–`led[7]` | M15, M14, M12, P14 | LVCMOS33 | Some online tutorials list M16/N16; those are wrong |
| `usb_rx` | P15 | LVCMOS33 | USB-serial, PC → FPGA |
| `usb_tx` | P16 | LVCMOS33 | USB-serial, FPGA → PC |

**Base constraints file (`au_v2.xdc`).** The top part maps ports to pins and tells Vivado the clock is 100 MHz so it can check timing. The bottom part tells Vivado how the board's flash chip is wired, so designs boot from flash the same way Alchitry's do.

```tcl
## Clock
set_property -dict {PACKAGE_PIN N14 IOSTANDARD LVCMOS33} [get_ports clk]
create_clock -period 10.000 -name clk [get_ports clk]

## Reset button (active low)
set_property -dict {PACKAGE_PIN P6 IOSTANDARD LVCMOS33} [get_ports rst_n]

## LEDs
set_property -dict {PACKAGE_PIN K13 IOSTANDARD LVCMOS33} [get_ports {led[0]}]
set_property -dict {PACKAGE_PIN K12 IOSTANDARD LVCMOS33} [get_ports {led[1]}]
set_property -dict {PACKAGE_PIN L14 IOSTANDARD LVCMOS33} [get_ports {led[2]}]
set_property -dict {PACKAGE_PIN L13 IOSTANDARD LVCMOS33} [get_ports {led[3]}]
set_property -dict {PACKAGE_PIN M15 IOSTANDARD LVCMOS33} [get_ports {led[4]}]
set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVCMOS33} [get_ports {led[5]}]
set_property -dict {PACKAGE_PIN M12 IOSTANDARD LVCMOS33} [get_ports {led[6]}]
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVCMOS33} [get_ports {led[7]}]

## USB-UART
set_property -dict {PACKAGE_PIN P15 IOSTANDARD LVCMOS33} [get_ports usb_rx]
set_property -dict {PACKAGE_PIN P16 IOSTANDARD LVCMOS33} [get_ports usb_tx]

## Configuration / flash settings (from Alchitry's au_props.xdc)
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property CFGBVS VCCO [current_design]
set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR NO [current_design]
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]
```

To see Alchitry's original files, build any Alchitry Labs project and look in its `build\constraint\` folder (`alchitry.xdc` and `au_props.xdc`). That folder is regenerated on every build, so always copy from it rather than pointing Vivado at it.

## Troubleshooting

When something fails, read the **first** error message, not the last. Most later errors are knock-on effects.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Alchitry build fails at once with "Vivado not found" or a path error | Vivado location points at the wrong folder | Set it to the `Vivado` folder with `bin` directly inside (Part 2) |
| `Part xc7a35t... not found` or not installed | Artix-7 support wasn't selected during install | Rerun the Vivado installer and add **Devices → 7 Series → Artix-7** |
| License error during build | Wrong Vivado edition | Install **Vivado ML Standard** (free) |
| Board not detected by Alchitry Labs or Vivado | Charge-only cable, or USB hub | Use a data cable, plugged straight into the PC |
| Board not detected on Linux | USB permissions | Install the udev rules from Alchitry / Vivado's cable driver script |
| Hardware Manager **Auto Connect** finds no target (Windows) | Cable drivers not installed | Close Vivado. In your install, open `...\Vivado\data\xicom\cable_drivers\nt64\` and run the `install_drivers` script **as administrator**, then replug the board. Meanwhile, use Alchitry Loader with the `.bin` |
| Vivado error: port has no pin location (`UCIO-1` / `NSTD-1`), bitstream refused | A port in `top.v` has no line in the `.xdc` | Add the pin, or remove the port; names must match exactly |
| Critical warning: `No ports matched 'usb_rx'` (or another name) | The `.xdc` names a port that `top.v` doesn't have | Add the port to `top.v` or delete that `.xdc` line |
| Build succeeds but LEDs do nothing | Wrong board selected (Au instead of Au V2), or something else drives `led` | Check board and code |
| Edits don't show up after rebuilding | Sources were copied into the project | Remove the file from Sources and re-add it with **Copy sources into project** unticked |
| LEDs look always on | Counter bits too low, so blinking is too fast to see | Use the top counter bits (`[26:19]`) |
| Timing summary shows negative WNS | Logic too slow for the clock | Rare for these tests; ask the team before going further |
| Only warning is TIMING-18 "missing input or output delay" on buttons/LEDs | Normal for slow signals | Safe to ignore for these pins |
