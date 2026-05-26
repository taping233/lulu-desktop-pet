[Version]
Class=IEXPRESS
SEDVersion=3

[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles

[Strings]
InstallPrompt=即将安装 lulu在摸鱼。
DisplayLicense=
FinishMessage=lulu在摸鱼 已安装完成。
TargetName=D:\素材\desktop_app\dist\lulu在摸鱼_Setup.exe
FriendlyName=lulu在摸鱼
AppLaunched=powershell.exe -NoProfile -ExecutionPolicy Bypass -File install.ps1

[SourceFiles]
SourceFiles0=D:\素材\desktop_app\installer\payload\

[SourceFiles0]
%FILE0%=lulu在摸鱼.exe
%FILE1%=install.ps1
%FILE2%=uninstall.ps1
%FILE3%=README.txt
