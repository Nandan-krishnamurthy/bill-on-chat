import asyncio
import re

# Test regex matching for numeric input
message = '1'
selection_match = re.match(r'^\s*(\d+)\s*$', message)
print(f'Message: "{message}"')
print(f'Matches numeric pattern: {bool(selection_match)}')
if selection_match:
    print(f'Selection number: {selection_match.group(1)}')

# Test regex matching for non-numeric
message2 = 'add product test'
selection_match2 = re.match(r'^\s*(\d+)\s*$', message2)
print(f'\nMessage: "{message2}"')
print(f'Matches numeric pattern: {bool(selection_match2)}')
