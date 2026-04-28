$content = (Invoke-WebRequest -Uri "https://vinegrape.ru/js/app.1fbc41d4.js" -UseBasicParsing).Content
$index = $content.IndexOf("vinegrape")
if ($index -ge 0) {
    Write-Host $content.Substring([Math]::Max(0, $index - 30), 100)
} else {
    Write-Host "Not found"
}
