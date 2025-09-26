// Theme toggle
const themeBtn = document.getElementById("theme-toggle");
themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light");
});

// ---------------- TRAIN STATUS ----------------
const trainBtn = document.getElementById("check-train");
trainBtn.addEventListener("click", () => {
    const trainNo = document.getElementById("train-no").value;
    fetch(`/train_status?train_no=${trainNo}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("train-name").innerText = data.train_name;
            document.getElementById("current-station").innerText = data.current_station;
            document.getElementById("next-station").innerText = data.next_station;
            document.getElementById("scheduled-arrival").innerText = data.scheduled_arrival;
            document.getElementById("delay-min").innerText = data.delay_minutes;
            document.getElementById("predicted-delay").innerText = data.predicted_delay;

            // 👇 Add delay reason if available
            if (data.delay_reason) {
                document.getElementById("delay-reason").innerText = data.delay_reason;
            } else {
                document.getElementById("delay-reason").innerText = "-";
            }

            document.getElementById("platform").innerText = data.platform;
        })
        .catch(err => console.error("Error fetching train status:", err));
});


// ---------------- WEATHER ----------------
const weatherBtn = document.getElementById("get-weather");
weatherBtn.addEventListener("click", () => {
    const city = document.getElementById("city").value;
    fetch(`/weather?city=${city}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("city-name").innerText = data.city;
            document.getElementById("temperature").innerText = data.temperature;
            document.getElementById("condition").innerText = data.condition;
            document.getElementById("humidity").innerText = data.humidity;
            document.getElementById("wind-speed").innerText = data.wind_speed;
        })
        .catch(err => console.error("Error fetching weather:", err));
});

// ---------------- SOS ----------------
function sendSOS(category) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            fetch(`/sos?lat=${position.coords.latitude}&lon=${position.coords.longitude}&category=${category}`, {
                method: 'POST'
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("sos-info").innerHTML = `
                    <p>Responder: ${data.responder_name}</p>
                    <p><a href="${data.link}" target="_blank">View on Map</a></p>
                `;
            })
            .catch(err => console.error("Error sending SOS:", err));
        }, error => {
            console.error("Geolocation error:", error);
            alert("Could not get your location.");
        });
    } else {
        alert("Geolocation not supported by your browser.");
    }
}
function sendEmergencyMessage() {
    alert("Emergency message sent to your emergency contact.");
}

// ---------------- DATE MODULE ----------------
function updateDate() {
    const today = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById("today-date").textContent = today.toLocaleDateString(undefined, options);
}

// Run once on load
updateDate();
