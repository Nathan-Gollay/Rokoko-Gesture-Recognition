"""
Web Demo of 360 Video Player
Author: Nathan Gollay, Unknown

CURRENTLY OBSOLETE
"""
# External Files
import webview

def main():
    webview.create_window(
        "360 Video Player",
        "360_video_player.html",
        width=800,
        height=600,
        resizable=True
    )
    webview.start()

if __name__ == "__main__":
    main()
