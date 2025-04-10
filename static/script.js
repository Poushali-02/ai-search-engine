function parseMarkdown(text) {
  return text
    // Escape HTML special characters
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")

    // Headings
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')

    // Bold
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')

    // Italic (after bold to prevent conflict)
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')

    // Inline code
    .replace(/`([^`]+)`/gim, '<code>$1</code>')

    // Line breaks
    .replace(/\n/g, '<br />');
}

// Load typing sound
const typingAudio = new Audio("https://www.soundjay.com/mechanical/typewriter-key-2.mp3");

document.getElementById("search-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const userInput = document.getElementById("user_input").value.trim();
  if (!userInput) return;

  const chatBox = document.getElementById("chat-box");

  const userMessage = document.createElement("div");
  userMessage.className = "message user";
  userMessage.innerHTML = `<div class="bubble"><strong>You:</strong> ${userInput}</div>`;
  chatBox.appendChild(userMessage);
  chatBox.scrollTop = chatBox.scrollHeight;

  document.getElementById("user_input").value = "";

  const botMessage = document.createElement("div");
  botMessage.className = "message bot";
  const botBubble = document.createElement("div");
  botBubble.className = "bubble typing";
  botBubble.innerHTML = `<em>Thinking...</em>`;
  botMessage.appendChild(botBubble);
  chatBox.appendChild(botMessage);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: userInput })
    });

    const data = await res.json();
    const parsedText = parseMarkdown(data.response || "Sorry, I couldn't respond.");

    // Typewriter effect with typing sound
    let i = 0;
    botBubble.innerHTML = "";
    botBubble.classList.add("typing");
    const typeChar = () => {
      if (i < parsedText.length) {
        botBubble.innerHTML += parsedText.charAt(i);
        typingAudio.pause();
        typingAudio.currentTime = 0;
        typingAudio.play().catch(() => {});
        i++;
        setTimeout(typeChar, 10); // speed
      } else {
        botBubble.classList.remove("typing");
      }
    };
    typeChar();

  } catch (err) {
    botBubble.innerHTML = `<div class="bubble"><strong>Error:</strong> Could not reach server.</div>`;
    console.error("Fetch error:", err);
  }
});
