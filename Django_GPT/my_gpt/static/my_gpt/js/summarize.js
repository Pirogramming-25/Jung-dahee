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
    if (text.length < 100) {
      showError(errorBox, "요약할 문서는 100자 이상 입력해주세요.");
      return;
    }
    if (text.length > 5000) {
      showError(errorBox, "문서는 5,000자 이하로 입력해주세요.");
      return;
    }

    setBusy(true, { button, textarea, processingEl });
    try {
      const { result } = await postJSON("/summarize/run/", { text });

      document.getElementById("original-length").textContent = result.original_length;
      document.getElementById("summary-length").textContent = result.summary_length;
      document.getElementById("summary-ratio").textContent = result.ratio.toFixed(2);
      document.getElementById("summary-text").textContent = result.summary;

      resultBox.classList.remove("hidden");
      pushHistoryItem(historyList, `${text.slice(0, 60)} → ${result.summary.slice(0, 60)}`);
    } catch (err) {
      showError(errorBox, err.message);
    } finally {
      setBusy(false, { button, textarea, processingEl });
    }
  });
})();
