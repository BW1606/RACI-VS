; Inno Setup script for RACI-VS Manager
; Prerequisites: run build.bat first so dist\RACI-VS\ exists.
; Install Inno Setup from https://jrsoftware.org/isinfo.php, then open this
; file in Inno Setup Compiler and click Build > Compile.

#define AppName      "RACI-VS Manager"
#define AppVersion   "1.0"
#define AppPublisher "Your Company"
#define AppExeName   "RACI-VS.exe"
#define SourceDir    "dist\RACI-VS"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\RACI-VS
DefaultGroupName={#AppName}
OutputBaseFilename=RACI-VS_Setup
Compression=lzma
SolidCompression=yes
; Install without requiring admin rights (per-user install)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
; Include all files from the PyInstaller output folder
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";     Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional, controlled by the Tasks section above)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch the app immediately after installation
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
