chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "CHECK_URL") {
    fetch("http://127.0.0.1:8000/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: msg.url }),
    })
      .then((r) => r.json())
      .then(sendResponse)
      .catch(() => sendResponse(null));
    return true; // ответ будет асинхронным
  }
});