// Shared helpers used by every feature's JS file.

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function postJSON(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(data),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload && payload.error ? payload.error : "모델 실행에 실패했습니다.\n잠시 후 다시 시도해주세요.";
    throw new Error(message);
  }
  return payload;
}

function setBusy(isBusy, { button, textarea, processingEl, extraButtons = [] }) {
  if (button) button.disabled = isBusy;
  if (textarea) textarea.disabled = isBusy;
  extraButtons.forEach((btn) => { if (btn) btn.disabled = isBusy; });
  if (processingEl) processingEl.classList.toggle("hidden", !isBusy);
}

function showError(errorBox, message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError(errorBox) {
  errorBox.classList.add("hidden");
  errorBox.textContent = "";
}

function formatPercent(score) {
  return (score * 100).toFixed(2) + "%";
}

function pushHistoryItem(listEl, text, emptyMessageMatch = "기록이 없습니다.") {
  const emptyItem = listEl.querySelector("li.empty-history");
  if (emptyItem) emptyItem.remove();

  const li = document.createElement("li");
  li.textContent = text;
  listEl.insertBefore(li, listEl.firstChild);

  while (listEl.children.length > 5) {
    listEl.removeChild(listEl.lastElementChild);
  }
}
