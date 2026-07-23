function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
}

const CSRF_TOKEN = getCookie("csrftoken");

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function formatPercent(score) {
    return `${(Number(score) * 100).toFixed(1)}%`;
}

async function postJSON(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRF_TOKEN,
        },
        body: JSON.stringify(payload),
    });

    let data = null;
    try {
        data = await response.json();
    } catch (err) {
        data = null;
    }

    if (!response.ok) {
        const message = data && data.error ? data.error : `요청 처리 중 오류가 발생했습니다. (${response.status})`;
        throw new Error(message);
    }

    return data;
}

function setBusy(button, textarea, isBusy, busyLabel) {
    if (isBusy) {
        button.dataset.originalLabel = button.dataset.originalLabel || button.textContent;
        button.textContent = busyLabel || "처리 중...";
        button.disabled = true;
        textarea.disabled = true;
    } else {
        button.textContent = button.dataset.originalLabel || button.textContent;
        button.disabled = false;
        textarea.disabled = false;
    }
}

function showResult(box, html) {
    box.classList.remove("is-hidden", "is-error");
    box.innerHTML = html;
}

function showError(box, message) {
    box.classList.remove("is-hidden");
    box.classList.add("is-error");
    box.textContent = message;
}
