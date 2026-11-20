"""Build-time retrieval of the specified self-hosted fonts and their OFL licences."""
import hashlib
import json
import urllib.request
from ml.config import ROOT

FILES = {
    'bricolage-latin.woff2': 'https://fonts.gstatic.com/s/bricolagegrotesque/v9/3y9H6as8bTXq_nANBjzKo3IeZx8z6up5BeSl5jBNz_19PpbpMXuECpwUxJBOm_OJWiawA1XphjhQYg.woff2',
    'figtree-latin.woff2': 'https://fonts.gstatic.com/s/figtree/v9/_Xms-HUzqDCFdgfMm4S9DaRvzig.woff2',
    'Bricolage-OFL.txt': 'https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/OFL.txt',
    'Figtree-OFL.txt': 'https://raw.githubusercontent.com/google/fonts/main/ofl/figtree/OFL.txt',
}


def main():
    destination = ROOT / 'app/static/fonts'
    downloaded = {}
    for name, url in FILES.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read(500_001)
        if len(content) > 500_000:
            raise ValueError('Unexpectedly large font asset.')
        if name.endswith('.woff2') and content[:4] != b'wOF2':
            raise ValueError('The font response was not WOFF2.')
        if name.endswith('.txt') and b'SIL OPEN FONT LICENSE' not in content:
            raise ValueError('The font licence was not the expected OFL.')
        downloaded[name] = content
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in downloaded.items():
        (destination/name).write_bytes(content)
    manifest = {name:{'source':FILES[name],'sha256':hashlib.sha256(content).hexdigest()}
                for name,content in downloaded.items()}
    (destination/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Saved two WOFF2 fonts and their licences; runtime font requests stay on the app origin.')


if __name__ == '__main__':
    main()
