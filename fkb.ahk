#Requires AutoHotkey v2.0
#NoTrayIcon
#SingleInstance Force
SetWorkingDir A_ScriptDir

if (A_Args.Length > 0) {
    tecla := A_Args[1]

    ; Só reporta ao servidor de teste se o arquivo de flag existir
    if (FileExist(A_ScriptDir "\fkb_test.flag")) {
        try {
            whr := ComObject("WinHttp.WinHttpRequest.5.1")
            whr.SetTimeouts(300, 300, 300, 300)
            whr.Open("POST", "http://localhost:9877", false)
            whr.SetRequestHeader("Content-Type", "text/plain")
            whr.Send(tecla)
        }
    }

    ; Envia o comando de teclado
    if (InStr(tecla, "{"))
        Send(tecla)
    else
        Send("{" tecla "}")
}

ExitApp
