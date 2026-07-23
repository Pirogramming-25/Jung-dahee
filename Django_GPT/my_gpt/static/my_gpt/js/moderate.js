(function () {
  const form = document.getElementById("run-form");
  const textarea = document.getElementById("input-text");
  const button = document.getElementById("run-button");
  const processingEl = document.getElementById("processing");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const historyList = document.getElementById("history-list");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideError(errorBox);

    const text = textarea.value.trim();
    if (!text) {
      showError(errorBox, "분석할 문장을 입력해주세요.");
      return;
    }

    setBusy(true, { button, textarea, processingEl });
    try {
      const { result } = await postJSON("/moderate/run/", { text });

      document.getElementById("highest-label").textContent = result.highest_label;
      document.getElementById("highest-score").textContent = formatPercent(result.highest_score);

      const allScoresEl = document.getElementById("result-all-scores");
      allScoresEl.innerHTML = "";
      result.all_scores.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.label}: ${formatPercent(item.score)}`;
        allScoresEl.appendChild(li);
      });

      resultBox.classList.remove("hidden");
      pushHistoryItem(historyList, `${text.slice(0, 60)} → ${result.highest_label} (${formatPercent(result.highest_score)})`);
    } catch (err) {
      showError(errorBox, err.message);
    } finally {
      setBusy(false, { button, textarea, processingEl });
    }
  });
})();
