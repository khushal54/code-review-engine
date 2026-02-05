async function review() {
  const code = document.getElementById("code").value;
  const language = document.getElementById("language").value;
  const output = document.getElementById("output");

  // Safety check
  if (!code.trim()) {
    output.textContent = "❌ Please paste some code to review.";
    return;
  }

  // Reset counters
  document.getElementById("criticalCount").textContent = 0;
  document.getElementById("highCount").textContent = 0;
  document.getElementById("mediumCount").textContent = 0;
  document.getElementById("lowCount").textContent = 0;

  output.textContent = "⏳ Analyzing code...";

  try {
    const response = await fetch("http://127.0.0.1:8000/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language })
    });

    const data = await response.json();

    if (!response.ok) {
      output.textContent = "❌ Error: " + (data.detail || "Unknown error");
      return;
    }

    const analysis = data.analysis;

    // Severity counters
    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;

    let resultText = `
${data.mode}

SUMMARY:
${analysis.summary}

ISSUES:
`;

    analysis.issues.forEach(issue => {
      resultText += `- [${issue.severity}] ${issue.type}: ${issue.message}\n`;

      if (issue.severity === "Critical") critical++;
      if (issue.severity === "High") high++;
      if (issue.severity === "Medium") medium++;
      if (issue.severity === "Low") low++;
    });

    resultText += `
RECOMMENDATIONS:
`;

    analysis.recommendations.forEach(rec => {
      resultText += `- ${rec}\n`;
    });

    resultText += `
OPTIMIZED CODE:
${analysis.optimized_code}
`;

    // Update UI
    document.getElementById("criticalCount").textContent = critical;
    document.getElementById("highCount").textContent = high;
    document.getElementById("mediumCount").textContent = medium;
    document.getElementById("lowCount").textContent = low;

    output.textContent = resultText.trim();

  } catch (error) {
    output.textContent =
      "❌ Failed to connect to backend. Make sure FastAPI server is running.";
  }
}
