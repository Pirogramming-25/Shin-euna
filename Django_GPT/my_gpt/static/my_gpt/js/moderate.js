(function () {
    const form = document.getElementById("moderate-form");
    if (!form) return;

    const textarea = document.getElementById("moderate-text");
    const button = document.getElementById("moderate-submit");
    const resultBox = document.getElementById("moderate-result");
    const charCount = document.getElementById("moderate-char-count");

    function updateCharCount() {
        if (charCount) charCount.textContent = textarea.value.length;
    }

    function renderResult(topLabel, allLabels) {
        const bars = allLabels
            .slice()
            .sort((a, b) => b.score - a.score)
            .map(
                (item) => `
                <div class="score-bar${item.label === topLabel.label ? " score-bar--danger" : ""}">
                    <div class="score-bar__head"><span>${escapeHtml(item.label)}</span><span>${formatPercent(item.score)}</span></div>
                    <div class="score-bar__track"><div class="score-bar__fill" style="width:${(item.score * 100).toFixed(1)}%"></div></div>
                </div>`
            )
            .join("");

        showResult(
            resultBox,
            `<div class="result-row"><span class="result-row__label">최고 위험 레이블</span><span>${escapeHtml(topLabel.label)} (${formatPercent(topLabel.score)})</span></div>
             ${bars}`
        );
    }

    textarea.addEventListener("input", updateCharCount);
    updateCharCount();

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const text = textarea.value.trim();

        if (!text) {
            showError(resultBox, "검사할 텍스트를 입력해주세요.");
            return;
        }
        if (text.length > 1000) {
            showError(resultBox, "텍스트는 1,000자 이내로 입력해주세요.");
            return;
        }

        setBusy(button, textarea, true);
        try {
            const data = await postJSON("/moderate/run/", { text });
            renderResult(data.top_label, data.result);
        } catch (err) {
            showError(resultBox, err.message);
        } finally {
            setBusy(button, textarea, false);
        }
    });
})();
