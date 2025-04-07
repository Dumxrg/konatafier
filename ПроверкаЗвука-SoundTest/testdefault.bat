@echo off
powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('Операция выполнена успешно.','Уведомление',[System.Windows.MessageBoxButton]::OK,[System.Windows.MessageBoxImage]::Information)"
exit