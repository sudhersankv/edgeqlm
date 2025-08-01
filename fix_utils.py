# Fix utils.py script
import sys

# Read the original file
with open('src/utils_backup.py', 'r') as f:
    content = f.read()

# Find where the mangled code starts and clean it
lines = content.split('\n')
clean_lines = []
for line in lines:
    if 'def create_banner' in line and 'str' in line:
        # Found the mangled function, stop here
        break
    clean_lines.append(line)

# Add the correct create_banner function
banner_func = '''

def create_banner(title: str, subtitle: str, version: str, features: List[str]) -> str:
    \
\\Create
a
formatted
banner
for
the
application\\\
    max_width = 80
    
    # Create banner lines
    banner_lines = []
    banner_lines.append(\\ + \\ * (max_width - 2) + \\)
    banner_lines.append(\\ + \
\ * (max_width - 2) + \║\)
    
    # Title
    title_padding = (max_width - 2 - len(title)) // 2
    banner_lines.append(\\ + \
\ * title_padding + title + \
\ * (max_width - 2 - title_padding - len(title)) + \\)
    
    # Subtitle
    subtitle_padding = (max_width - 2 - len(subtitle)) // 2
    banner_lines.append(\\ + \
\ * subtitle_padding + subtitle + \
\ * (max_width - 2 - subtitle_padding - len(subtitle)) + \\)
    
    # Version
    version_line = f\Version:
version
\
    version_padding = (max_width - 2 - len(version_line)) // 2
    banner_lines.append(\\ + \
\ * version_padding + version_line + \
\ * (max_width - 2 - version_padding - len(version_line)) + \\)
    
    banner_lines.append(\\ + \
\ * (max_width - 2) + \\)
    
    # Features
    if features:
        for feature in features:
            feature_padding = (max_width - 2 - len(feature)) // 2
            banner_lines.append(\\ + \
\ * feature_padding + feature + \
\ * (max_width - 2 - feature_padding - len(feature)) + \\)
    
    banner_lines.append(\\ + \
\ * (max_width - 2) + \\)
    banner_lines.append(\\ + \\ * (max_width - 2) + \\)
    
    return '\n'.join(banner_lines)
'''

# Write the fixed file
with open('src/utils.py', 'w') as f:
    f.write('\n'.join(clean_lines))
    f.write(banner_func)

print(' Fixed utils.py successfully')

