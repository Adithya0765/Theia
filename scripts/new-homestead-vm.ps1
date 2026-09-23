# Homestead VM creator (Windows + VirtualBox).
# Usage: .\scripts\new-homestead-vm.ps1 -IsoPath "C:\...\homestead.iso"
param([Parameter(Mandatory = $true)][string]$IsoPath)

$VBM = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$VM = "homestead"

if (-not (Test-Path -LiteralPath $IsoPath)) {
  Write-Error "ISO not found: $IsoPath (build it in Kali first, see docs/windows-vbox-loop.md)"
  exit 1
}

# Idempotent: delete previous VM of the same name if present.
& $VBM showvminfo $VM *> $null
if ($?) { & $VBM unregistervm $VM --delete }

& $VBM createvm --name $VM --ostype "Linux26_64" --register
& $VBM modifyvm $VM --memory 2048 --cpus 2 --firmware efi --chipset piix3 `
  --graphicscontroller vmsvga --vram 64 --accelerate3d on `
  --nic1 nat --audio-driver none --boot1 dvd --boot2 disk
& $VBM storagectl $VM --name "IDE" --add ide --controller PIIX4
& $VBM storageattach $VM --storagectl "IDE" --port 0 --device 0 `
  --type dvddrive --medium $IsoPath
& $VBM storagectl $VM --name "SATA" --add sata --controller IntelAhci
& $VBM createhd --filename "$env:USERPROFILE\VirtualBox VMs\$VM\$VM.vdi" --size 8192 --format VDI
& $VBM storageattach $VM --storagectl "SATA" --port 0 --device 0 `
  --type hdd --medium "$env:USERPROFILE\VirtualBox VMs\$VM\$VM.vdi"

Write-Output "VM '$VM' ready. Start it in VirtualBox; checklist: os/iso/VBOX-TEST.md"
