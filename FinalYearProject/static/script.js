function sendMessage() {
    let userMessage = document.getElementById("userInput").value;
    if (!userMessage.trim()) return;

    fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        let chatbox = document.getElementById("chatbox");
        chatbox.innerHTML += `<p>User: ${userMessage}</p>`;
        chatbox.innerHTML += `<p>Bot: ${data.response}</p>`;

        // Bot speaks the response and changes animation
        speak(data.response);
    });

    document.getElementById("userInput").value = "";
}

// Function for speech synthesis (Text-to-Speech)
function speak(text) {
    let speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.volume = 1;
    speech.rate = 1;
    speech.pitch = 1;

    // Change bot image to speaking animation
    document.getElementById("botImage").src = "/static/bot_speaking.gif";

    speech.onend = function() {
        // Change back to idle image after speaking
        document.getElementById("botImage").src = "/static/bot_idle.png";
    };

    window.speechSynthesis.speak(speech);
}

// Function for voice input (Speech-to-Text)
function startListening() {
    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = function(event) {
        let userMessage = event.results[0][0].transcript;
        document.getElementById("userInput").value = userMessage;
        sendMessage();
    };
}


document.getElementById("facultyBtn").addEventListener("click", function () {
    document.getElementById("facultyLinks").classList.toggle("show");
});
