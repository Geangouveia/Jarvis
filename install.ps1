# =====================================================================
# J.A.R.V.I.S. — INSTALADOR E EXECUTOR AUTOMÁTICO EM 1 CLIQUE
# Funciona em qualquer computador Windows com acesso à internet.
# =====================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   J.A.R.V.I.S. - PROTOCOLO DE INSTALACAO RAPIDA        " -ForegroundColor Cyan
Write-Host "   Stark Industries Operating System (PC Edition)       " -ForegroundColor DarkCyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$dest = "$HOME\Desktop\Jarvis"
$zipUrl = "https://github.com/Geangouveia/Jarvis/archive/refs/heads/main.zip"
$zipFile = "$env:TEMP\jarvis_temp.zip"
$extractDir = "$env:TEMP\jarvis_extract"

Write-Host "[1/4] Baixando a versao mais recente do GitHub..." -ForegroundColor Yellow
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing

Write-Host "[2/4] Extraindo arquivos para a sua Area de Trabalho..." -ForegroundColor Yellow
if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue }
Expand-Archive -Path $zipFile -DestinationPath $extractDir -Force

if (-not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

Copy-Item -Path "$extractDir\Jarvis-main\*" -Destination $dest -Recurse -Force

# Limpeza de temporários
Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "[3/4] Arquivos configurados em: $dest" -ForegroundColor Green
Write-Host "[4/4] Inicializando o J.A.R.V.I.S...." -ForegroundColor Cyan
Write-Host ""

# Inicia o run_jarvis.bat diretamente
Start-Process -FilePath "cmd.exe" -ArgumentList "/c run_jarvis.bat" -WorkingDirectory $dest

Write-Host "========================================================" -ForegroundColor Green
Write-Host "  J.A.R.V.I.S. INSTALADO E EM EXECUCAO COM SUCESSO!     " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
