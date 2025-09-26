function sendEmergencyMessage() {
    const emergencyNumber = document.getElementById("emergency").value;
    const message = "This is an emergency message.";
    fetch(`/send_emergency_message?to=${emergencyNumber}&message=${encodeURIComponent(message)}`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        alert("Emergency message sent!");
    })
    .catch(err => console.error("Error sending emergency message:", err));
}
