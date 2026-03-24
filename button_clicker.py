# 작성일 : 2026.3.24.
# 작성자 : doo & Gemini 3 Flash(Antigravity)
import pyautogui
import time
import os
import sys
import argparse
import subprocess

try:
    from AppKit import NSScreen
    import Quartz.CoreGraphics as CG
    from PIL import Image
except ImportError:
    NSScreen = None

def get_monitors():
    """PyAutoGUI 좌표계에서 모니터 기하학 정보를 (left, top, width, height, displayID) 목록으로 반환"""
    if not NSScreen:
        w, h = pyautogui.size()
        return [(0, 0, w, h, None)]
    
    screens = NSScreen.screens()
    if not screens:
        w, h = pyautogui.size()
        return [(0, 0, w, h, None)]
        
    primary_screen = screens[0]
    primary_h = primary_screen.frame().size.height
    
    monitors = []
    for screen in screens:
        frame = screen.frame()
        device_description = screen.deviceDescription()
        display_id = device_description.get('NSScreenNumber')
        
        # AppKit(좌측 하단 기준, Y축 위쪽) 좌표를 PyAutoGUI(좌측 상단 기준, Y축 아래쪽) 좌표로 변환
        left = int(frame.origin.x)
        top = int(primary_h - (frame.origin.y + frame.size.height))
        width = int(frame.size.width)
        height = int(frame.size.height)
        monitors.append((left, top, width, height, display_id))
    
    return monitors

def capture_screen_quartz(display_id):
    """Quartz를 사용하여 특정 디스플레이를 캡처하고 PIL 이미지를 반환"""
    image_ref = CG.CGDisplayCreateImage(display_id)
    if not image_ref:
        return None
    
    width = CG.CGImageGetWidth(image_ref)
    height = CG.CGImageGetHeight(image_ref)
    
    data_provider = CG.CGImageGetDataProvider(image_ref)
    data = CG.CGDataProviderCopyData(data_provider)
    
    # 원본 BGRA 데이터(Quartz 표준)로 PIL 이미지 생성
    img = Image.frombuffer('RGBA', (width, height), data, 'raw', 'BGRA', 0, 1)
    
    return img.convert('RGB')

def capture_target(target_path):
    """macOS의 screencapture -i 명령어를 사용하여 대상 이미지를 캡처합니다."""
    print(f"\n[!] 캡처 모드를 시작합니다: '{target_path}'")
    print("마우스로 클릭-드래그하여 대상을 선택하세요. (취소하려면 Esc)")
    
    try:
        # macOS screencapture 대화형 모드(-i) 사용
        # -x: 셔터 소음 비활성화
        result = subprocess.run(["screencapture", "-i", "-x", target_path], check=True)
        
        if os.path.exists(target_path):
            print(f"    캡처 성공: '{target_path}' 저장됨.")
            return True
        else:
            print("    캡처가 취소되었거나 파일이 저장되지 않았습니다.")
            return False
    except subprocess.CalledProcessError:
        print("    캡처 중 오류가 발생했습니다.")
        return False
    except Exception as e:
        print(f"    캡처 오류: {e}")
        return False

def cursor_area_clicker(target_path):
    if not os.path.exists(target_path):
        print(f"오류: '{target_path}' 파일이 현재 디렉토리에 없습니다.")
        print("먼저 --capture 옵션을 사용하여 이미지를 생성하거나 기존 이미지를 지정하세요.")
        return

    print(f"'{target_path}' 감시를 시작합니다. (Quartz 기반 고성능 캡처)")
    print("마우스 커서 주변 400x400 영역을 실시간으로 감시합니다.")
    print("이미지 발견 시 3초 후에 클릭합니다. (Confidence: 0.7)")
    print("중단하려면 터미널에서 Ctrl+C를 누르세요.")
    
    try:
        monitors = get_monitors()
        print(f"감지된 모니터: {len(monitors)}개")
        for i, m in enumerate(monitors):
            print(f"  모니터 {i+1}: {m[2]}x{m[3]} (위치: {m[0]}, {m[1]}, ID: {m[4]})")

        last_search_time = time.time()
        
        while True:
            # 1. 현재 마우스 위치 가져오기 (전역 좌표)
            x, y = pyautogui.position()
            
            # 2. 마우스 주변 탐색 영역 설정
            search_size = 400 
            search_left = x - search_size // 2
            search_top = y - search_size // 2
            
            found = False
            for m_left, m_top, m_width, m_height, display_id in monitors:
                # 탐색 영역과 모니터 경계의 교차 영역 계산
                inter_left = max(search_left, m_left)
                inter_top = max(search_top, m_top)
                inter_right = min(search_left + search_size, m_left + m_width)
                inter_bottom = min(search_top + search_size, m_top + m_height)
                
                if inter_right > inter_left and inter_bottom > inter_top:
                    try:
                        # Quartz를 사용하여 디스플레이 캡처
                        screen_img = capture_screen_quartz(display_id)
                        if not screen_img:
                            continue
                            
                        # Retina 스케일링 처리
                        scale_x = screen_img.width / m_width
                        scale_y = screen_img.height / m_height
                        
                        # 로컬 영역으로 자르기
                        crop_left = (inter_left - m_left) * scale_x
                        crop_top = (inter_top - m_top) * scale_y
                        crop_right = (inter_right - m_left) * scale_x
                        crop_bottom = (inter_bottom - m_top) * scale_y
                        
                        crop_region = screen_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                        
                        # 이미지 찾기
                        match = pyautogui.locate(target_path, crop_region, confidence=0.7)
                        
                        if match:
                            # 전역 좌표로 다시 매핑
                            found_x_rel = (crop_left + (match.left + match.width/2)) / scale_x
                            found_y_rel = (crop_top + (match.top + match.height/2)) / scale_y
                            
                            found_x = m_left + found_x_rel
                            found_y = m_top + found_y_rel
                            
                            distance = ((found_x - x)**2 + (found_y - y)**2)**0.5
                            
                            print(f"\n[!] 이미지({target_path}) 감지! (위치: {found_x:.0f}, {found_y:.0f}, 거리: {distance:.0f}px)")
                            print("    3초 후에 클릭 시퀀스를 시작합니다...")
                            time.sleep(3)
                            
                            # 클릭 직전 마우스 위치 저장
                            orig_x, orig_y = pyautogui.position()
                            
                            # 속도를 위해 일시적으로 일시 정지(PAUSE)를 0으로 설정
                            old_pause = pyautogui.PAUSE
                            pyautogui.PAUSE = 0
                            
                            # 클릭 수행
                            pyautogui.click(found_x, found_y) 
                            
                            # 원래 위치로 즉시 복구
                            pyautogui.moveTo(orig_x, orig_y)
                            
                            # 설정 복구
                            pyautogui.PAUSE = old_pause
                            
                            print("    클릭 완료 및 마우스 위치 복구!")
                            
                            time.sleep(2) # 대기 시간 (Cooldown)
                            found = True
                            break
                    except Exception:
                        pass
            
            if not found:
                if time.time() - last_search_time > 3:
                    print(".", end="", flush=True)
                    last_search_time = time.time()
                time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"치명적 오류 발생: {e}")
        print("※ Mac 설정 > 개인정보 보호 및 보안 > 화면 기록 / 손쉬운 사용 권한을 다시 한 번 확인하세요.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quartz 기반 고성능 이미지 감지 클릭커")
    parser.add_argument("target", nargs="?", default="button.jpg", help="감지할 이미지 파일 경로 (기본값: button.jpg)")
    parser.add_argument("--capture", "-c", action="store_true", help="타겟 이미지를 직접 캡처하여 저장")
    
    args = parser.parse_args()
    
    pyautogui.FAILSAFE = True
    
    if args.capture:
        if not capture_target(args.target):
            sys.exit(1)
            
    cursor_area_clicker(args.target)
