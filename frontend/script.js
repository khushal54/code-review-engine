const API_URL = "http://127.0.0.1:8000";

window.onload = checkApiStatus;

async function checkApiStatus() {
  const statusEl = document.getElementById("apiStatus");

  try {
    const res = await fetch(API_URL);
    if (res.ok) {
      statusEl.textContent = "● API Connected";
      statusEl.className = "text-green-400 text-sm";
    } else {
      throw new Error();
    }
  } catch {
    statusEl.textContent = "● API Disconnected";
    statusEl.className = "text-red-400 text-sm";
  }
}

async function review() {
  const code = document.getElementById("code").value;
  const language = document.getElementById("language").value;
  const output = document.getElementById("output");
  const optimizedBox = document.getElementById("optimizedCode");

  if (!code.trim()) {
    output.textContent = "❌ Please paste some code to review.";
    return;
  }

  // Reset
  output.textContent = "⏳ Analyzing code...";
  optimizedBox.textContent = "Waiting for optimized output...";

  document.getElementById("criticalCount").textContent = 0;
  document.getElementById("highCount").textContent = 0;
  document.getElementById("mediumCount").textContent = 0;
  document.getElementById("lowCount").textContent = 0;

  try {
    const res = await fetch(`${API_URL}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language })
    });

    const data = await res.json();

    const analysis = data.analysis;
    let critical = 0, high = 0, medium = 0, low = 0;

    let text = `${data.mode}\n\nSUMMARY:\n${analysis.summary}\n\nISSUES:\n`;

    analysis.issues.forEach(issue => {
      text += `- [${issue.severity}] ${issue.type}: ${issue.message}\n`;
      if (issue.severity === "Critical") critical++;
      if (issue.severity === "High") high++;
      if (issue.severity === "Medium") medium++;
      if (issue.severity === "Low") low++;
    });

    text += "\nRECOMMENDATIONS:\n";
    analysis.recommendations.forEach(r => text += `- ${r}\n`);

    output.textContent = text.trim();
    optimizedBox.textContent = analysis.optimized_code;

    document.getElementById("criticalCount").textContent = critical;
    document.getElementById("highCount").textContent = high;
    document.getElementById("mediumCount").textContent = medium;
    document.getElementById("lowCount").textContent = low;

  } catch {
    output.textContent = "❌ Backend not reachable.";
  }
}

function copyOptimized() {
  const text = document.getElementById("optimizedCode").textContent;
  navigator.clipboard.writeText(text);
   alert("✅ Optimized code copied to clipboard!");
}
