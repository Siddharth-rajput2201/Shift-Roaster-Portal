document.getElementById("ptoForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;

    // Example AJAX call to send PTO request to the backend
    fetch("/api/pto", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ startDate, endDate })
    })
    .then(response => response.json())
    .then(data => {
        // Handle successful PTO request submission
        alert("PTO request submitted successfully!");
    })
    .catch(error => {
        console.error("Error submitting PTO request:", error);
    });
});

// Function to fetch notifications
function fetchNotifications() {
    fetch("/api/notifications")
        .then(response => response.json())
        .then(data => {
            const notificationList = document.getElementById("notificationList");
            notificationList.innerHTML = ""; // Clear existing notifications
            data.notifications.forEach(notification => {
                const li = document.createElement("li");
                li.textContent = notification.message;
                notificationList.appendChild(li);
            });
        });
}

// Call fetchNotifications on dashboard load
if (document.getElementById("notificationList")) {
    fetchNotifications();
}

document.getElementById("signupForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const username = document.querySelector("#signupForm input[type='text']").value;
    const password = document.querySelector("#signupForm input[type='password']").value;
    const role = document.querySelector("#signupForm input[type='text']:nth-of-type(2)").value;

    // Example AJAX call to send signup request to the backend
    fetch("/api/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password, role })
    })
    .then(response => response.json())
    .then(data => {
        // Handle successful signup
        if (data.success) {
            alert("Sign up successful! You can now log in.");
            window.location.href = "index.html"; // Redirect to login
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error signing up:", error);
    });
});