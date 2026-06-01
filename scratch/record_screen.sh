#!/bin/bash
# ============================================================
#   CloudSense — macOS Screen Recording Utility (via ffmpeg)
# ============================================================
#   This script automates screen recording on your Mac.
#   It records your main display in 1080p high quality.
# ============================================================

# Color settings
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}   CloudSense — macOS Screen Recorder Utility (ffmpeg)       ${NC}"
echo -e "${CYAN}============================================================${NC}"
echo -e "This script will record your main screen to help you build your video."
echo ""
echo -e "Choose your recording mode:"
echo -e "  [1] ${GREEN}Screen + Microphone Audio${NC} (Explain your project in French)"
echo -e "  [2] ${GREEN}Screen ONLY (Silent)${NC} (Perfect for adding AI voiceover later)"
echo ""
read -p "Enter choice [1 or 2]: " choice

OUTPUT_FILE="scratch/my_demo_capture.mp4"

if [ "$choice" == "1" ]; then
    echo -e "${YELLOW}🎙️ Mode: Screen + Microphone active.${NC}"
    echo -e "Ensure your microphone isn't muted. Output will be saved to: ${CYAN}$OUTPUT_FILE${NC}"
    echo -e "${RED}👉 Press 'q' at any time inside this terminal to STOP recording.${NC}"
    echo ""
    read -p "Press [ENTER] to START recording..."
    echo -e "${GREEN}🔴 RECORDING ACTIVE...${NC}"
    
    ffmpeg -f avfoundation -i "1:0" -r 30 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k "$OUTPUT_FILE" -y

else
    echo -e "${YELLOW}🤫 Mode: Screen Only (Silent).${NC}"
    echo -e "Output will be saved to: ${CYAN}$OUTPUT_FILE${NC}"
    echo -e "${RED}👉 Press 'q' at any time inside this terminal to STOP recording.${NC}"
    echo ""
    read -p "Press [ENTER] to START recording..."
    echo -e "${GREEN}🔴 RECORDING ACTIVE (SILENT)...${NC}"
    
    ffmpeg -f avfoundation -i "1:" -r 30 -c:v libx264 -pix_fmt yuv420p "$OUTPUT_FILE" -y
fi

echo ""
echo -e "${GREEN}✅ Recording stopped and saved successfully!${NC}"
echo -e "File location: [my_demo_capture.mp4](file://$(pwd)/$OUTPUT_FILE)"
echo -e "You can now use CapCut or Canva to overlay your AI English voiceover."
