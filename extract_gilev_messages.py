import os
import re
import html

def parse_html_files(directory):
    files = sorted([f for f in os.listdir(directory) if f.startswith('messages') and f.endswith('.html')], 
                   key=lambda x: int(x.replace('messages', '').replace('.html', '') or 1))
    
    gilev_messages = []
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find message blocks
        # This is a bit fragile but might work given the consistent formatting
        # We'll split by <div class="message default clearfix" to get chunks
        chunks = content.split('<div class="message default clearfix"')
        
        for chunk in chunks[1:]: # Skip preamble
            # Extract ID (not strictly needed but good for reference)
            id_match = re.search(r'id="message(\d+)"', 'id="message' + chunk[:20])
            msg_id = id_match.group(1) if id_match else "unknown"
            
            # Extract Date
            date_match = re.search(r'class="pull_right date details" title="([\d\.]+ [\d:]+)', chunk)
            date_str = date_match.group(1) if date_match else ""
            
            # Extract Sender
            from_match = re.search(r'<div class="from_name">\s*(.*?)\s*</div>', chunk, re.DOTALL)
            sender = from_match.group(1).strip() if from_match else ""
            
            # Extract Text
            text_match = re.search(r'<div class="text">\s*(.*?)\s*</div>', chunk, re.DOTALL)
            text = text_match.group(1).strip() if text_match else ""
            
            # Filter
            if "gilev.ru" in sender or "Gilev" in sender:
                # Parse date year
                # Format: 02.03.2026 11:05:49
                try:
                    year = int(date_str.split('.')[2].split()[0])
                    if year >= 2024:
                        # Clean text (remove HTML tags)
                        clean_text = re.sub(r'<br\s*/?>', '\n', text)
                        clean_text = re.sub(r'<[^>]+>', '', clean_text)
                        clean_text = html.unescape(clean_text)
                        
                        gilev_messages.append({
                            'id': msg_id,
                            'date': date_str,
                            'sender': sender,
                            'text': clean_text,
                            'file': filename
                        })
                except Exception as e:
                    # print(f"Error parsing date: {date_str} in {filename}")
                    pass

    return gilev_messages

if __name__ == "__main__":
    msgs = parse_html_files('.')
    print(f"Found {len(msgs)} messages from gilev.ru since 2024.")
    
    # Sort by date (oldest to newest seems to be the file order, but let's be sure)
    # Actually the files are numbered, messages inside are chronological.
    # So the list should be roughly sorted.
    
    with open('gilev_extracted.txt', 'w', encoding='utf-8') as f:
        for msg in msgs:
            f.write(f"--- MSG {msg['id']} ({msg['date']}) ---\n")
            f.write(f"{msg['text']}\n\n")
            
    print("Messages saved to gilev_extracted.txt")
