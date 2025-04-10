document.getElementById("search-form").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const userInput = document.getElementById("user_input").value;
    const responseBox = document.getElementById("response-box");
    responseBox.innerHTML = "<em>Thinking...</em>";
  
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: userInput })
    });
  
    const data = await res.json();
  
    responseBox.innerHTML = `<strong>Gemini:</strong> ${data.response}`;
  });
  