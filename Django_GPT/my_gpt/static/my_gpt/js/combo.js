(function () {
    const form = document.getElementById("combo-form");
    if (!form) return;

    const textarea = document.getElementById("combo-text");
    const button = document.getElementById("combo-submit");
    const resultBox = document.getElementById("combo-result");
    const charCount = document.getElementById("combo-char-count");
    const regenerateButton = document.getElementById("combo-regenerate");

    const MIN_LENGTH = 200;
    const MAX_LENGTH = 5000;

    let lastText = "";

    function updateCharCount() {
        if (charCount) charCount.textContent = textarea.value.length;
    }

    function renderResult(originalText, data) {
        const sentiment = data.sentiment || {};
        const toxicity = data.toxicity || {};
        const allScores = (toxicity.all_scores || [])
            .slice()
            .sort((a, b) => b.score - a.score);

        const bars = allScores
            .map(
                (item) => `
                <div class="score-bar${item.label === toxicity.highest_label ? " score-bar--danger" : ""}">
                    <div class="score-bar__head"><span>${escapeHtml(item.label)}</span><span>${formatPercent(item.score)}</span></div>
                    <div class="score-bar__track"><div class="score-bar__fill" style="width:${(item.score * 100).toFixed(1)}%"></div></div>
                </div>`
            )
            .join("");

        showResult(
            resultBox,
            `<div class="result-row" style="flex-direction:column;align-items:flex-start;">
                <span class="result-row__label">입력 원문</span>
                <span>${escapeHtml(originalText)}</span>
             </div>
             <div class="result-row" style="flex-direction:column;align-items:flex-start;">
                <span class="result-row__label">요약</span>
                <span>${escapeHtml(data.summary || "-")}</span>
             </div>
             <div class="result-row"><span class="result-row__label">감정 분석</span><span>${escapeHtml(sentiment.label || "-")} (${formatPercent(sentiment.score || 0)})</span></div>
             <div class="result-row"><span class="result-row__label">유해 표현 · 최고 위험 레이블</span><span>${escapeHtml(toxicity.highest_label || "-")} (${formatPercent(toxicity.highest_score || 0)})</span></div>
             ${bars}
             <div class="result-row" style="flex-direction:column;align-items:flex-start;border-top:1px dashed var(--color-border);margin-top:0.5rem;padding-top:0.5rem;">
                <span class="result-row__label">종합 판정</span>
                <span>${escapeHtml(data.verdict || "-")}</span>
             </div>`
        );

        regenerateButton.style.display = "inline-flex";
    }

    async function runPipeline(text) {
        setBusy(button, textarea, true);
        regenerateButton.disabled = true;
        try {
            const data = await postJSON("/combo/run/", { text });
            lastText = text;
            renderResult(text, data);
        } catch (err) {
            showError(resultBox, err.message);
        } finally {
            setBusy(button, textarea, false);
            regenerateButton.disabled = false;
        }
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
        if (text.length < MIN_LENGTH || text.length > MAX_LENGTH) {
            showError(resultBox, `텍스트는 ${MIN_LENGTH}~${MAX_LENGTH}자 사이로 입력해주세요.`);
            return;
        }

        await runPipeline(text);
    });

    regenerateButton.addEventListener("click", async function () {
        if (!lastText) return;
        await runPipeline(lastText);
    });
})();
