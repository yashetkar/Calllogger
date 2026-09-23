Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Run the Flask server silently in the background
WshShell.Run "pythonw app.py", 0, False

' Give the Flask server 1.5 seconds to start up
WScript.Sleep 1500

chromePath = ""
paths = Array(_
    "C:\Program Files\Google\Chrome\Application\chrome.exe",_
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",_
    WshShell.ExpandEnvironmentStrings("%LocalAppData%") & "\Google\Chrome\Application\chrome.exe"_
)

For Each p In paths
    If fso.FileExists(p) Then
        chromePath = p
        Exit For
    End If
Next

If chromePath <> "" Then
    ' Launch Google Chrome in standalone App Mode
    WshShell.Run """" & chromePath & """ --app=http://127.0.0.1:5000", 1, False
Else
    ' Fallback to Microsoft Edge in standalone App Mode
    WshShell.Run "msedge --app=http://127.0.0.1:5000", 1, False
End If
