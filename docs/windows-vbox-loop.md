# Windows ↔ Kali build-to-boot loop (VirtualBox on Windows)

You are here: Windows host, VirtualBox 7.x, one Kali guest.
Builds run **inside Kali** (Buildroot needs Linux). Boots run in a **new
Homestead VM on Windows**. The ISO is the handoff artefact.

```
Windows (this machine, assistant runs here)
  C:\My Files\Projects\Theia\  <- repo
    os/            <- build specs (authored here)
    output/        <- homestead.iso lands here (from Kali)
    scripts/       <- VM creation scripts (run here)
         ↕ shared folder / copy
Kali VM (VirtualBox guest)
  ~/Theia          <- repo copy (git clone or shared folder)
  ./os/build.sh    <- produces output/homestead.iso
```

## 1. Build (inside Kali)

```bash
sudo apt update && sudo apt install -y git make gcc g++ bc bison flex \
  libncurses-dev libssl-dev cpio unzip rsync wget xorriso \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools qemu-system-x86
cd ~/Theia
./os/build.sh virtualbox
ls -lh output/   # want: homestead.iso
```

Fast smoke test before touching VirtualBox:

```bash
qemu-system-x86_64 -m 2048 -cdrom output/homestead.iso -boot d
```

## 2. Move ISO to Windows

Pick one (easiest first):

- **VirtualBox shared folder:** Devices → Shared Folders → add
  `C:\My Files\Projects\Theia\output` as `theia-out`, auto-mount; in Kali
  `sudo mount -t vboxsf theia-out ~/Theia/output` (needs Guest Additions).
- **Quick HTTP:** in Kali `cd ~/Theia/output && python3 -m http.server 8000`,
  on Windows browse `http://<kali-ip>:8000/homestead.iso`.
- **scp:** `scp user@<kali-ip>:~/Theia/output/homestead.iso output/`.

## 3. Boot (on Windows, scripted)

```powershell
# once per new ISO:
.\scripts\new-homestead-vm.ps1 -IsoPath "C:\My Files\Projects\Theia\output\homestead.iso"
# then start Homestead VM in VirtualBox and follow os/iso/VBOX-TEST.md
```

Rebuilding is just: edit `os/` here → sync to Kali → rebuild → re-copy ISO →
boot same VM (no need to recreate it).
