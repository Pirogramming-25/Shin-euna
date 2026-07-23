(function () {
    const form = document.getElementById("sentiment-form");
    if (!form) return;

    const textarea = document.getElementById("sentiment-text");
    const button = document.getElementById("sentiment-submit");
    const resultBox = document.getElementById("sentiment-result");
    const charCount = document.getElementById("sentiment-char-count");
    const historyList = document.getElementById("sentiment-history-anon");
    const isAuthenticated = form.dataset.authenticated === "1";

    let anonHistory = [];

    function updateCharCount() {
        if (charCount) charCount.textContent = textarea.value.length;
    }

    function renderResult(label, score) {
        showResult(
            resultBox,
            `<div class="result-row"><span class="result-row__label">레이블</span><span>${escapeHtml(label)}</span></div>
             <div class="score-bar">
                <div class="score-bar__head"><span>신뢰도</span><span>${formatPercent(score)}</span></div>
                <div class="score-bar__track"><div class="score-bar__fill" style="width:${(score * 100).toFixed(1)}%"></div></div>
             </div>`
        );
    }

    function renderAnonHistory() {
        if (!historyList) return;
        if (anonHistory.length === 0) {
            historyList.innerHTML = '<li class="history-empty">아직 기록이 없습니다.</li>';
            return;
        }
        historyList.innerHTML = anonHistory
            .map(
                (item) =>
                    `<li><span class="history-text">${escapeHtml(item.text)}</span><span class="history-meta">${escapeHtml(item.label)} (${formatPercent(item.score)})</span></li>`
            )
            .join("");
    }

    textarea.addEventListener("input", updateCharCount);
    updateCharCount();

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const text = textarea.value.trim();

        if (!text) {
            showError(resultBox, "분석할 텍스트를 입력해주세요.");
            return;
        }
        if (text.length > 1000) {
            showError(resultBox, "텍스트는 1,000자 이내로 입력해주세요.");
            return;
        }

        setBusy(button, textarea, true);
        try {
            const data = await postJSON("/sentiment/run/", { text });
            renderResult(data.label, data.score);

            if (!isAuthenticated) {
                anonHistory.unshift({ text, label: data.label, score: data.score });
                anonHistory = anonHistory.slice(0, 5);
                renderAnonHistory();
            }
        } catch (err) {
            showError(resultBox, err.message);
        } finally {
            setBusy(button, textarea, false);
        }
    });
})();
