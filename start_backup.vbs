Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "C:\Users\mokht\OneDrive\Desktop\Automatic folder backup\folder_Backup"
shell.Run """C:\Users\mokht\OneDrive\Desktop\Automatic folder backup\venvback\Scripts\pythonw.exe"" ""C:\Users\mokht\OneDrive\Desktop\Automatic folder backup\folder_Backup\main.py""", 0, False