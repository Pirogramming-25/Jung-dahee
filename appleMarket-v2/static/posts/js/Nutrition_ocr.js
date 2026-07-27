// 영양 성분표 이미지를 업로드하면 비동기로 OCR 서버에 전송하고,
// 결과가 오면 calories/carbohydrate/protein/fat 폼 필드를 자동으로 채운다.
// 채워진 값은 일반 input이므로 사용자가 직접 수정할 수 있다.

function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
}

document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('nutrition_photo');
    const statusEl = document.getElementById('ocr_status');
    const previewEl = document.getElementById('nutrition_preview');

    if (!fileInput) return;

    fileInput.addEventListener('change', async function () {
        const file = fileInput.files[0];
        if (!file) return;

        // 미리보기
        if (previewEl) {
            previewEl.src = URL.createObjectURL(file);
            previewEl.style.display = 'block';
        }

        if (statusEl) {
            statusEl.textContent = '분석 중...';
            statusEl.style.display = 'inline';
        }

        const formData = new FormData();
        formData.append('image', file);

        const ocrUrl = fileInput.dataset.ocrUrl;

        try {
            const response = await fetch(ocrUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData,
            });

            const rawText = await response.text();
            let data;
            try {
                data = JSON.parse(rawText);
            } catch (parseErr) {
                // 서버가 JSON이 아닌 응답(HTML 에러 페이지 등)을 준 경우
                console.error('JSON 파싱 실패, 서버 응답 원문:', rawText);
                if (statusEl) {
                    statusEl.textContent = response.status === 404
                        ? '분석 실패: OCR 주소를 찾을 수 없습니다 (404). urls.py 설정을 확인해주세요.'
                        : `분석 실패: 서버가 JSON이 아닌 응답을 반환했습니다 (status ${response.status}). 콘솔을 확인해주세요.`;
                }
                return;
            }

            if (!response.ok || data.error) {
                if (statusEl) statusEl.textContent = '분석 실패: ' + (data.error || '알 수 없는 오류');
                return;
            }

            const fieldMap = {
                calories: 'id_calories',
                carbohydrate: 'id_carbohydrate',
                protein: 'id_protein',
                fat: 'id_fat',
            };

            let filledCount = 0;
            for (const [key, elId] of Object.entries(fieldMap)) {
                const el = document.getElementById(elId);
                if (el && data[key] !== null && data[key] !== undefined) {
                    el.value = data[key];
                    filledCount += 1;
                }
            }

            if (statusEl) {
                statusEl.textContent = filledCount > 0
                    ? `분석 완료! ${filledCount}개 항목이 자동으로 채워졌습니다. (필요 시 직접 수정하세요)`
                    : '분석은 완료됐지만 항목을 찾지 못했습니다. 직접 입력해주세요.';
            }
        } catch (err) {
            if (statusEl) statusEl.textContent = '분석 중 오류가 발생했습니다: ' + err;
        }
    });
});