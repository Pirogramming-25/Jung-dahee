"""
영양 성분표 이미지에서 칼로리 / 탄수화물 / 단백질 / 지방을 추출하는 유틸.
PaddleOCR을 사용하며, 인식률을 높이기 위해 전처리(그레이스케일 -> 업스케일 -> 이진화)를 거친다.
"""
import re
import numpy as np
from PIL import Image
import cv2

# PaddleOCR 초기화는 비용이 크므로 모듈 최초 1회만 로드 (lazy singleton)
_ocr_instance = None


def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR
        # lang='korean' : 한글 영양성분표 지원, use_angle_cls: 회전된 텍스트 보정
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang='korean', show_log=False)
    return _ocr_instance


def _preprocess(image_file):
    """업로드된 이미지 파일(InMemoryUploadedFile)을 OCR 인식률이 잘 나오도록 전처리.
    이진화(threshold)는 소수점처럼 작은 디테일을 뭉갤 수 있어 사용하지 않고,
    업스케일 + 샤프닝 + 대비 향상(CLAHE) 정도로만 처리한다."""
    pil_img = Image.open(image_file).convert('RGB')
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # 1. 그레이스케일
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 업스케일 (작은 글씨/소수점 인식률 향상). LANCZOS4가 CUBIC보다
    #    글자 외곽선을 더 또렷하게 보존해 g/9 같은 혼동을 조금 줄여준다.
    h, w = gray.shape
    target_min_dim = 2000
    if min(h, w) < target_min_dim:
        scale = target_min_dim / min(h, w)
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)

    # 3. 언샤프 마스크로 글자 외곽선 강조 (뭉개진 곡선을 좀 더 뚜렷하게)
    blurred = cv2.GaussianBlur(gray, (0, 0), sigmaX=2)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)

    # 4. 대비 향상 (CLAHE) - 이진화 없이 글자와 배경의 대비만 살짝 높여서
    #    작은 점(소수점)이 뭉개지지 않도록 함
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(sharpened)

    # PaddleOCR은 3채널 입력을 기대하므로 다시 BGR로 변환

    processed = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    return processed


# 키워드 -> (모델 필드명, 기본 단위)
_KEYWORDS = {
    'calories': (['칼로리', '열량'], 'kcal'),
    'carbohydrate': (['탄수화물'], 'g'),
    'protein': (['단백질'], 'g'),
    'fat': (['지방'], 'g'),
}

# 숫자 + (선택적) 단위 패턴. 쉼표 천단위 구분자도 허용 (예: 1,500)
_NUMBER_PATTERN = re.compile(r'([\d,]+\.?\d*)\s*(kcal|mg|g)?', re.IGNORECASE)

# 하단 "1일 영양성분 기준치..." 같은 안내 문구는 '열량', '기준치' 등의 단어를 포함해
# 오탐(예: "2,000kcal 기준"을 실제 칼로리로 착각)을 일으키므로 제외 대상으로 둔다.
_DISCLAIMER_HINTS = ['기준치', '기준으로', '기준입니다', '필요 열량', '다를 수 있습니다']


def _normalize_to_g(value: float, unit: str) -> float:
    if unit and unit.lower() == 'mg':
        return round(value / 1000, 1)
    return round(value, 1)


# '지방' 키워드가 '트랜스지방'/'포화지방'/'불포화지방'의 일부로 오매칭되는 것을 방지
_FAT_KEYWORD_PATTERN = re.compile(r'(?<!트랜스)(?<!포화)(?<!불포화)지방')


def _line_has_keyword(line, field, keywords):
    if field == 'fat':
        return bool(_FAT_KEYWORD_PATTERN.search(line))
    return any(kw in line for kw in keywords)


def _best_value_after_label(text):
    """라벨 뒤 텍스트에서 값으로 쓸 숫자를 찾는다.
    1) g/mg 단위가 명확히 붙은 숫자를 최우선으로 채택
    2) 없으면(OCR이 단위 글자를 숫자로 오인식한 경우 등) '%'가 바로 뒤에 붙지 않는
       첫 숫자를 채택 (퍼센트 값과 혼동 방지)
    3) 그래도 없으면 그냥 첫 번째 숫자"""
    matches = list(_NUMBER_PATTERN.finditer(text))
    if not matches:
        return None
    for m in matches:
        if m.group(2) and m.group(2).lower() in ('g', 'mg'):
            return m.group(1), m.group(2)
    for m in matches:
        tail = text[m.end():m.end() + 1]
        if tail != '%':
            return m.group(1), m.group(2)
    return matches[0].group(1), matches[0].group(2)


def _parse_labeled(full_text_lines):
    """'칼로리', '탄수화물' 등 명시적 라벨 옆의 숫자를 파싱.
    행 단위로 이미 정렬되어 있으므로 같은 행 안에서만 값을 찾는다
    (다른 행까지 넘어가면 다른 영양성분 값을 잘못 가져올 위험이 있어 하지 않음)."""
    result = {'calories': None, 'carbohydrate': None, 'protein': None, 'fat': None}

    for field, (keywords, default_unit) in _KEYWORDS.items():
        for line in full_text_lines:
            if any(h in line for h in _DISCLAIMER_HINTS):
                continue
            if not _line_has_keyword(line, field, keywords):
                continue

            if field == 'fat':
                kw_match = _FAT_KEYWORD_PATTERN.search(line)
                after_kw = line[kw_match.end():] if kw_match else line
            else:
                after_kw = line
                for kw in keywords:
                    if kw in line:
                        after_kw = line.split(kw, 1)[1]
                        break

            found = _best_value_after_label(after_kw)
            if found:
                num_str, unit = found
                try:
                    value = float(num_str.replace(',', ''))
                except ValueError:
                    continue
                unit = unit or default_unit
                if field == 'calories':
                    result[field] = int(round(value))
                else:
                    result[field] = _normalize_to_g(value, unit)
                break
    return result


def _fallback_calories(full_text_lines):
    """'390 kcal' 처럼 라벨 없이 숫자+kcal만 단독으로 적힌 경우를 위한 보조 탐색.
    '390' 과 'kcal' 이 서로 다른 줄로 분리되는 경우도 있고, OCR이 'kcal'의 마지막 글자를
    깨뜨리는 경우도 많아(예: 'kca!', 'kcaI') 'kca' 까지만 일치하면 인정한다.
    안내 문구(예: '2,000kcal 기준')는 제외하고, 읽는 순서상 가장 먼저 나오는 값을 채택한다."""
    pattern = re.compile(r'([\d,]+\.?\d*)\s*kca', re.IGNORECASE)
    number_only_pattern = re.compile(r'^([\d,]+\.?\d*)$')
    bare_kcal_pattern = re.compile(r'^kca', re.IGNORECASE)

    for idx, line in enumerate(full_text_lines):
        if any(h in line for h in _DISCLAIMER_HINTS):
            continue

        # 케이스 1: 한 줄에 숫자+kcal(오인식 포함)이 같이 있는 경우
        match = pattern.search(line)
        if match:
            try:
                return int(round(float(match.group(1).replace(',', ''))))
            except ValueError:
                pass

        # 케이스 2: 숫자만 있는 줄 다음(또는 이전)에 'kcal'(오인식 포함)만 있는 줄이 오는 경우
        num_match = number_only_pattern.match(line.strip())
        if num_match:
            neighbors = []
            if idx + 1 < len(full_text_lines):
                neighbors.append(full_text_lines[idx + 1])
            if idx - 1 >= 0:
                neighbors.append(full_text_lines[idx - 1])
            if any(bare_kcal_pattern.match(n.strip()) for n in neighbors):
                try:
                    return int(round(float(num_match.group(1).replace(',', ''))))
                except ValueError:
                    pass
    return None


def _parse_lines(lines):
    """OCR로 추출된 텍스트 라인 리스트에서 4대 영양정보를 정규식으로 파싱."""
    full_text_lines = list(lines)
    result = _parse_labeled(full_text_lines)

    if result['calories'] is None:
        result['calories'] = _fallback_calories(full_text_lines)

    return result


def _group_into_rows(boxes):
    """OCR 텍스트 박스들을 y좌표(세로 위치) 기준으로 같은 행끼리 묶고,
    각 행 안에서는 x좌표(가로 위치) 기준으로 왼쪽->오른쪽 순서로 정렬한다.
    2열 표에서 라벨과 값이 텍스트 순서상 뒤섞이는 문제를 좌표 정보로 바로잡기 위함."""
    if not boxes:
        return []
    sorted_boxes = sorted(boxes, key=lambda b: b['y'])
    rows = [[sorted_boxes[0]]]
    for b in sorted_boxes[1:]:
        prev = rows[-1][-1]
        # 큰 글씨(예: '130 kcal') 박스 하나 때문에 병합 기준이 커져서
        # 위/아래의 다른 줄까지 같은 행으로 잘못 합쳐지는 것을 막기 위해
        # 두 박스 중 더 작은 높이를 기준으로 삼는다.
        threshold = min(prev['h'], b['h']) * 0.6
        if abs(b['y'] - prev['y']) <= threshold:
            rows[-1].append(b)
        else:
            rows.append([b])
    for row in rows:
        row.sort(key=lambda b: b['x'])
    return rows


def extract_nutrition_from_image(image_file) -> dict:
    """
    Django UploadedFile을 받아 {'calories':.., 'carbohydrate':.., 'protein':.., 'fat':..} 반환.
    값을 찾지 못한 항목은 None.
    """
    processed_img = _preprocess(image_file)
    ocr = _get_ocr()
    ocr_result = ocr.ocr(processed_img, cls=True)

    boxes = []
    if ocr_result and ocr_result[0]:
        for box, (text, conf) in ocr_result[0]:
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            boxes.append({
                'text': text,
                'x': sum(xs) / len(xs),
                'y': sum(ys) / len(ys),
                'h': max(ys) - min(ys),
            })

    rows = _group_into_rows(boxes)
    # 같은 행에 속한 텍스트를 왼쪽->오른쪽 순서로 이어붙여, 라벨과 그 옆 값이
    # 한 줄에 같이 오도록 만든다 (2열 표에서도 라벨=값 짝이 흐트러지지 않음)
    lines = [' '.join(b['text'] for b in row) for row in rows]

    parsed = _parse_lines(lines)
    parsed['raw_text'] = lines  # 디버깅/확인용 (프론트에서 필요 없으면 무시)
    return parsed