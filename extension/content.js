const checked = new Map();

function scan() {
  document.querySelectorAll("a[href^='http']").forEach((a) => {
    const url = a.href;
    if (new URL(url).hostname.endsWith("lalafo.kg") || a.dataset.asChecked) return;
    a.dataset.asChecked = "1";
    chrome.runtime.sendMessage({ type: "CHECK_URL", url }, (res) => {
      if (!res || res.score < 50) return;
      a.style.outline = "3px solid red";
      a.title = `⚠ Риск ${res.score}/100: ${res.reasons.join("; ")}`;
      a.addEventListener("click", (e) => {
        if (!confirm(`Внимание! Ссылка похожа на мошенническую.\n${res.reasons.join("\n")}\n\nВсё равно перейти?`)) {
          e.preventDefault();
        }
      });
    });
  });
}

new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
scan();