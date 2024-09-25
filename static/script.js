let video;

function init() {
    video = document.getElementById("video");

    // Initialize the webcam only for registration and login pages
    if (document.getElementById("canvas")) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(error => {
                console.log("Error accessing webcam:", error);
                alert("Cannot access webcam");
            });
    }

    // Attach event listener for the diagnose button if it exists
    const startDiagnoseButton = document.getElementById('start-diagnose-button');
    if (startDiagnoseButton) {
        startDiagnoseButton.addEventListener('click', startDiagnose);
    }

    // Attach event listener for the chatbot button if it exists
    const chatbotButton = document.getElementById('start-chatbot-button');
    if (chatbotButton) {
        chatbotButton.addEventListener('click', startChatbot);
    }

    // Attach event listener for the response submission button if it exists
    const submitResponseButton = document.getElementById('submit-response-button');
    if (submitResponseButton) {
        submitResponseButton.addEventListener('click', submitChatbotResponse);
    }

    // Attach event listener for the text response submission button if it exists
    const submitTextResponseButton = document.getElementById('submit-text-response-button');
    if (submitTextResponseButton) {
        submitTextResponseButton.addEventListener('click', submitTextResponse);
    }

    
}

function startDiagnose() {
    fetch('/start_diagnose', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Trigger the actual diagnosis process (e.g., face/emotion analysis)
            console.log('Diagnosis started.');

            // Once diagnosis is completed, fetch to complete the diagnose
            fetch('/finish_diagnose', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show the chatbot button after diagnosis is completed
                    document.getElementById('start-chatbot-button').style.display = 'inline';
                }
            })
            .catch(error => {
                console.error('Error finishing diagnosis:', error);
            });
        }
    })
    .catch(error => {
        console.error('Error starting diagnosis:', error);
    });
}

function register() {
    const nameInput = document.getElementById("nameInput");
    if (!nameInput) {
        alert("Name is required");
        return;
    }

    const name = nameInput.value;
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const photo = dataURItoBlob(canvas.toDataURL());

    const formData = new FormData();
    formData.append("name", name);
    formData.append("photo", photo, `${name}.jpg`);

    fetch("/register", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("Registration successful");
            window.location.href = data.redirect;
        } else {
            alert("Registration failed: " + (data.message || "Unknown error"));
        }
    })
    .catch(error => {
        console.log("Error:", error);
        alert("An error occurred: " + error.message);
    });
}

function login() {
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const photo = dataURItoBlob(canvas.toDataURL());

    const formData = new FormData();
    formData.append("photo", photo, "login.jpg");

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = "/success?name=" + encodeURIComponent(data.name) + "&image_path=" + encodeURIComponent(data.image_path);
        } else {
            alert("Login failed: " + (data.message || "Unknown error"));
        }
    })
    .catch(error => {
        console.log("Error:", error);
        alert("An error occurred: " + error.message);
    });
}

function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(",")[1]);
    const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

function startChatbot() {
    fetch('/chatbot')
    .then(response => response.text())
    .then(() => {
        // Redirect to the chatbot.html page where the conversation will happen
        window.location.href = "/chatbot_page";
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Failed to start chatbot.");
    });
}

function submitChatbotResponse() {
    const responseElement = document.querySelector('input[name="response"]:checked');
    if (!responseElement) {
        alert("Please select a response.");
        return;
    }

    const response = responseElement.value;

    fetch('/chatbot_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.question) {
            document.getElementById('chatbot-question').innerText = data.question;
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Failed to handle response.");
    });
}



window.onload = init;
