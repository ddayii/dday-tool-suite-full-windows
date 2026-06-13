; DDay Controls Tool Suite — Inno Setup Installer Script
; -------------------------------------------------------
; Prerequisites:
;   1. Run build_all.bat first to produce the EXEs in the dist\ folder.
;   2. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php
;   3. Open this file in Inno Setup Compiler and click Build > Compile
;      (or right-click the .iss in Explorer and choose "Compile")
;   Output: installer\DDay Controls Tool Suite Setup 2.1.2.exe

#define AppName      "DDay Controls Tool Suite"
#define AppVersion   "2.1.2"
#define AppPublisher "DDay Controls"
#define AppURL       ""
#define DistDir      "dist"
#define LauncherExe  "DDay Controls Tool Suite.exe"

[Setup]
; Unique identifier for this application — DO NOT reuse in other products.
AppId={{7B0038D1-27D7-4A04-B980-BB469DDE28DE}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Installation directory
; {autopf} = Program Files for admin install, %LOCALAPPDATA%\Programs for per-user
DefaultDirName={autopf}\{#AppPublisher}
DefaultGroupName={#AppPublisher}
AllowNoIcons=yes

; Allow the user to choose between per-user and machine-wide at install time
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Output
OutputDir=installer
OutputBaseFilename=DDay Controls Tool Suite Setup {#AppVersion}
SetupIconFile=DDay Logo.ico

; Compression
Compression=lzma2
SolidCompression=yes

; Appearance
WizardStyle=modern

; Automatically close running instances before installing
CloseApplications=yes
CloseApplicationsFilter=*.exe

; Uninstaller icon shown in Add/Remove Programs
UninstallDisplayIcon={app}\{#LauncherExe}
UninstallDisplayName={#AppName}


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"


[Types]
Name: "full";   Description: "Full Installation — all tools"
Name: "custom"; Description: "Custom Installation";           Flags: iscustom


[Components]
; Launcher is always required — users cannot deselect it
Name: "launcher";  Description: "Tool Suite Launcher (required)";                        Types: full custom; Flags: fixed
Name: "converter"; Description: "Conversion Tool — Unit, Scalar, Byte Stream & ASCII";  Types: full
Name: "ascii";     Description: "ASCII Chart — Character Code Reference Table";          Types: full
Name: "fanuc";     Description: "FANUC I/O Tool — Robot Comment Templates & KAREL";      Types: full


[Files]
; Launcher — always installed
Source: "{#DistDir}\{#LauncherExe}";                      DestDir: "{app}"; Components: launcher;  Flags: ignoreversion

; Individual tools — installed only when the matching component is selected
Source: "{#DistDir}\DDay Controls Conversion Tool.exe";   DestDir: "{app}"; Components: converter; Flags: ignoreversion
Source: "{#DistDir}\DDay Controls ASCII Chart.exe";        DestDir: "{app}"; Components: ascii;     Flags: ignoreversion
Source: "{#DistDir}\DDay Controls FANUC IO Tool.exe";      DestDir: "{app}"; Components: fanuc;     Flags: ignoreversion


[Icons]
; Start Menu — Launcher always present
Name: "{group}\{#AppName}";          Filename: "{app}\{#LauncherExe}"

; Start Menu — individual tools, shown only when installed
Name: "{group}\Conversion Tool";     Filename: "{app}\DDay Controls Conversion Tool.exe";  Components: converter
Name: "{group}\ASCII Chart";         Filename: "{app}\DDay Controls ASCII Chart.exe";       Components: ascii
Name: "{group}\FANUC IO Tool";       Filename: "{app}\DDay Controls FANUC IO Tool.exe";     Components: fanuc

; Start Menu — Uninstall
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop shortcut for the Launcher (optional task)
Name: "{autodesktop}\{#AppName}";    Filename: "{app}\{#LauncherExe}"; Tasks: desktopicon


[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut for the Launcher"; GroupDescription: "Additional shortcuts:"


[Run]
; Offer to launch the suite immediately after install
Filename: "{app}\{#LauncherExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent


[UninstallDelete]
; Remove any empty DDay Controls folder left behind after uninstall
Type: dirifempty; Name: "{app}"
