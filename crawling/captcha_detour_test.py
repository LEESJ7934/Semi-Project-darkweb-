


















# driver.get("http://threeamkelxicjsaf2czjyz2lc4q3ngqkxhhlexyfcp2o6raw4rphyad.onion/")  
# time.sleep(2)  
# #2. ocr을 통한 단순 시계 이미지 캡챠 우회 방법 진행중
# # 캡차 이미지 불러오기
# captcha_image = driver.find_element(By.CSS_SELECTOR, "img.m-auto")
# captcha_image.screenshot("clock_image.png")
# # 이미지 전처리
# gray = cv2.cvtColor("clock_image.png", cv2.COLOR_BGR2GRAY)  # 그레이스케일 변환
# _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)  # 이진화

# # 원 중심 찾기
# center = (thresh.shape[1] // 2, thresh.shape[0] // 2)

# # 시침과 분침의 각도 계산 함수
# def get_angle(line):
#     """주어진 선분의 각도를 계산"""
#     dx, dy = line[1][0] - line[0][0], line[1][1] - line[0][1]
#     angle = atan2(dy, dx)
#     return degrees(angle) % 360  # 각도 범위 [0, 360)

# # Hough 변환을 사용하여 직선 찾기 (시침, 분침)
# lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

# # 시침과 분침 찾기
# minute_hand_angle = 0
# hour_hand_angle = 0

# for line in lines:
#     for x1, y1, x2, y2 in line:
#         angle = get_angle([(x1, y1), (x2, y2)])
#         if abs(angle - 90) < 15:  # 분침이 90도 (3시 방향)
#             minute_hand_angle = angle
#         elif abs(angle - 0) < 15 or abs(angle - 180) < 15:  # 시침이 12시~1시 사이
#             hour_hand_angle = angle

# # 시간 계산
# minute = round(minute_hand_angle / 6)  # 360도에서 60분이므로 6도씩 차이
# hour = round(hour_hand_angle / 30)  # 360도에서 12시간이므로 30도씩 차이

# if minute == 0:
#     minute = 60

# # 텍스트로 시간 출력
# print(f"현재 시간은 {hour}시 {minute}분입니다.")
