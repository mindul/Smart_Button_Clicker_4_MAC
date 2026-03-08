import pyautogui
import time
import os
import sys

def cursor_area_clicker():
    # Use command line argument if provided, otherwise default to button.jpg
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        print("사용법: python button_clicker.py [이미지파일명]")
        return
    # else:
    #     target_path = "button.jpg"
    
    # if not os.path.exists(target_path):
    #     print(f"오류: '{target_path}' 파일이 현재 디렉토리에 없습니다.")
    #     if len(sys.argv) == 1:
    #         print("사용법: python button_clicker.py [이미지파일명]")
    #     return

    print(f"'{target_path}' 감시를 시작합니다.")
    print("마우스 커서 주변 200x200 영역을 실시간으로 감시합니다.")
    print("이미지 발견 시 3초 후에 클릭합니다.")
    print("중단하려면 터미널에서 Ctrl+C를 누르세요.")
    
    try:
        while True:
            # 1. Get current mouse position
            x, y = pyautogui.position()
            
            # 2. Define monitoring region (200x200 centered on cursor)
            size = 100
            left = max(0, x - size)
            top = max(0, y - size)
            width = min(pyautogui.size().width - left, size * 2)
            height = min(pyautogui.size().height - top, size * 2)
            
            # 3. Search for the target image only within this region
            try:
                location = pyautogui.locateOnScreen(target_path, region=(left, top, width, height), confidence=0.8)
                
                if location:
                    print(f"이미지({target_path}) 발견! 3초 후에 클릭합니다...")
                    time.sleep(3)
                    
                    print(f"클릭 실행: ({x}, {y})")
                    pyautogui.click(x, y)
                    
                    # Cooldown
                    time.sleep(1.5)
            except Exception:
                pass
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    cursor_area_clicker()
