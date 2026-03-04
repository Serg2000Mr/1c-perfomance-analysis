$files = Get-ChildItem "messages*.html" | Sort-Object { 
    if ($_.Name -match 'messages(\d+)\.html') {
        [int]$matches[1] 
    } else { 
        0 
    }
}

$output = @()

foreach ($file in $files) {
    # Read file content
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Split by message start div to iterate through messages
    # Using regex split might be slow on large files, but manageable here
    $chunks = $content -split '<div class="message default clearfix"'
    
    foreach ($chunk in $chunks) {
        # Check sender
        # The sender is in <div class="from_name">...</div>
        # We use regex with single line mode (?s) to handle newlines
        if ($chunk -match '(?s)<div class="from_name">\s*(.*?)\s*</div>') {
            $sender = $matches[1].Trim()
            
            # Check if sender is gilev.ru
            if ($sender -like "*gilev.ru*" -or $sender -like "*Вячеслав*") {
                
                # Extract date from title attribute: title="02.03.2026 11:05:49 UTC+03:00"
                if ($chunk -match 'title="(\d{2})\.(\d{2})\.(\d{4})') {
                    $year = [int]$matches[3]
                    
                    if ($year -ge 2024) {
                        # Extract text
                        if ($chunk -match '(?s)<div class="text">\s*(.*?)\s*</div>') {
                            $text = $matches[1]
                            
                            # Simple HTML cleanup
                            $text = $text -replace '<br\s*/?>', "`n"
                            $text = $text -replace '<[^>]+>', ''
                            $text = $text -replace '&quot;', '"'
                            $text = $text -replace '&lt;', '<'
                            $text = $text -replace '&gt;', '>'
                            $text = $text -replace '&amp;', '&'
                            $text = $text.Trim()
                            
                            if ($text.Length -gt 0) {
                                $output += "--- MSG DATE: $($matches[1]).$($matches[2]).$year ---"
                                $output += $text
                                $output += ""
                            }
                        }
                    }
                }
            }
        }
    }
}

$output | Out-File "gilev_extracted.txt" -Encoding UTF8
Write-Host "Extracted $($output.Count) messages to gilev_extracted.txt"
