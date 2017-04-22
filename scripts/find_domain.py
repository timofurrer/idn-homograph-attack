"""
Find a domain name which can be constructed
by only using a given set of characters.
In this case these characters are those which look
similar in the cyrillic and latin alphabet and thus
can be used for a IDN homograph attack.
"""

import sys
import csv
import codecs
import subprocess

cyrillic_latin_match = {
    'a': 'а',
    'e': 'е',
    'h': 'һ',
    'i': 'і',
    'j': 'ј',
    'l': 'ӏ',
    'o': 'о',
    'p': 'р',
    'r': 'г',
    's': 'ѕ',
    'w': 'ԝ',
    'x': 'х',
    'y': 'у'
}


def parse_domains(filename):
    """
    Parse a CSV file with domains
    in the format of:
        Rank, URL, Linking Root Domains, External Links, mozRank, mozTrust

    Download CSV from: https://moz.com/top500/domains/csv
    """
    print('Parsing domains from {0}'.format(filename))
    domains = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            url = row[1]
            if url == 'URL':  # that's the header
                continue
            domain_name, tld = url.rstrip('/').rsplit('.', maxsplit=1)
            domains.append((domain_name, tld))

    return domains


def match(domains, characters, only_available=False):
    """
    Match if one of the given domains only
    consists of the given character set.
    """
    for domain_name, tld in domains:
        if set(domain_name).issubset(characters):

            cyrillic_name = ''
            for c in domain_name:
                cyrillic_name += cyrillic_latin_match[c]

            punycode = codecs.encode(cyrillic_name, 'punycode').decode('utf-8')
            punycode_url = f'xn--{punycode}.{tld}'

            try:
                subprocess.check_call(['whois', punycode_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                is_registered = False
            else:
                is_registered = True

            if is_registered and only_available:
                continue

            available = '✗' if is_registered else '✓'

            print(f'{available} --> found {domain_name}.{tld} -> {cyrillic_name}.{tld} (Punycode: {punycode_url}) (unicode: {cyrillic_name.encode("utf-8")})')


if __name__ == '__main__':
    domains = parse_domains(sys.argv[1])
    match(domains, cyrillic_latin_match.keys(), only_available='--only-available' in sys.argv)
