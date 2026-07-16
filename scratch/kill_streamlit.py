import subprocess

try:
    print("Buscando e terminando processos do Streamlit com Get-CimInstance...")
    # Executa a busca e encerramento de processos python com 'streamlit' no comando
    cmd = 'Get-CimInstance Win32_Process -Filter "Name LIKE \'python%\'" | Where-Object { $_.CommandLine -like \'*streamlit*\' } | ForEach-Object { Write-Output "Matando PID: $_.ProcessId"; Stop-Process -Id $_.ProcessId -Force }'
    result = subprocess.run(
        ["powershell", "-Command", cmd],
        capture_output=True,
        text=True
    )
    print("Saída do PowerShell:")
    print(result.stdout)
    if result.stderr:
        print("Erros do PowerShell:")
        print(result.stderr)
except Exception as e:
    print("Erro ao tentar matar o processo:", e)
