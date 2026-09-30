import urllib.request
import urllib.error
import base64
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

files = ['diagrama_bd']

for f in files:
    with open(f'{f}.mmd', 'r', encoding='utf-8') as file:
        code = file.read()
    
    # Mermaid.ink format
    payload = {
        "code": code,
        "mermaid": {"theme": "default"}
    }
    json_payload = json.dumps(payload).encode('utf-8')
    b64_encoded = base64.urlsafe_b64encode(json_payload).decode('utf-8')
    
    url = f"https://mermaid.ink/img/{b64_encoded}?type=png"
    print(f"Downloading {url} ...")
    
    req = urllib.request.Request(
        url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/png,*/*;q=0.8'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            with open(f'{f}.png', 'wb') as out_file:
                out_file.write(response.read())
        print(f'Successfully downloaded {f}.png')
    except urllib.error.HTTPError as e:
        print(f'Failed to download {f}.png: HTTP {e.code} - {e.reason}')
    except Exception as e:
        print(f'Failed to download {f}.png: {e}')
