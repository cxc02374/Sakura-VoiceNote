#define MyAppName "Sakura VoiceNote"
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\\dist\\windows\\SakuraVoiceNote"
#endif
#ifndef InstallerIconFile
  #define InstallerIconFile "..\\assets\\voicenote_icon.ico"
#endif

[Setup]
AppId={{6A453CE1-A6E1-4A65-A1E1-8FA2B6C507A9}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher=Sakura Project
DefaultDirName={autopf}\Sakura VoiceNote
DefaultGroupName=Sakura VoiceNote
OutputDir=..\dist\installer
OutputBaseFilename=SakuraVoiceNote_Setup_{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile={#InstallerIconFile}
UninstallDisplayIcon={app}\SakuraVoiceNote.exe

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Sakura VoiceNote"; Filename: "{app}\SakuraVoiceNote.exe"
Name: "{commondesktop}\Sakura VoiceNote"; Filename: "{app}\SakuraVoiceNote.exe"

[Run]
Filename: "{app}\SakuraVoiceNote.exe"; Description: "Sakura VoiceNote を起動"; Flags: nowait postinstall skipifsilent
