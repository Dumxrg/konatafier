@echo off
powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('This is a test','Test',[System.Windows.MessageBoxButton]::OK,[System.Windows.MessageBoxImage]::Information)"
exit
