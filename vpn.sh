#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title vpn
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🤖

# Documentation:
# @raycast.author fevirtus
# @raycast.authorURL https://raycast.com/fevirtus

#!/bin/bash

# Mở Terminal và chạy lệnh vpn
osascript -e 'tell application "Terminal"
    do script "vpn"
end tell'

