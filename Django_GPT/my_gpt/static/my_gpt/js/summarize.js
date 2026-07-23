(function () {
    const form = document.getElementById("summarize-form");
    if (!form) return;

    const textarea = document.getElementById("summarize-text");
    const button = document.getElementById("summarize-submit");
    const resultBox = document.getElementById("summarize-result");
    const charCount = document.getElementById("summarize-char-count");

    function updateCharCount() {
        if (charCount) charCount.textContent = textarea.value.length;
    }

    function renderResult(summary, originalLength, summaryLength) {
        const ratio = originalLength > 0 ? ((summaryLength / originalLength) * 100).toFixed(1) : "0.0";
        showResult(
            resultBox,
            `<div class="result-row"><span class="result-row__label">원문 길이</span><span>${originalLength}자</span></div>
             <div class="result-row"><span class="result-row__label">요약문 길이</span><span>${summaryLength}자</span></div>
             <div class="result-row"><span class="result-row__label">요약 비율</span><span>${ratio}%</span></div>
             <div class="result-row" style="flex-direction:column;align-items:flex-start;">
                <span class="result-row__label">요약 결과</span>
                <span>${escapeHtml(summary)}</span>
             </div>`
        );
    }

    textarea.addEventListener("input", updateCharCount);
    updateCharCount();

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const text = textarea.value.trim();

        if (!text) {
            showError(resultBox, "요약할 텍스트를 입력해주세요.");
            return;
        }
        if (text.length < 100 || text.length > 5000) {
            showError(resultBox, "텍스트는 100~5,000자 사이로 입력해주세요.");
            return;
        }

        setBusy(button, textarea, true);
        try {
            const data = await postJSON("/summarize/run/", { text });
            renderResult(data.summary, data.original_length, data.summary_length);
        } catch (err) {
            showError(resultBox, err.message);
        } finally {
            setBusy(button, textarea, false);
        }
    });
})();
