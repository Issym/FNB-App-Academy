let rootPath = "https://mysite.itvarsity.org/api/ContactBook/";
let apiKey = localStorage.getItem("apiKey") || "appacademy@itvarsity.org";

// If no API key is saved, redirect to API key page
if (!apiKey) {
    window.open("enter-api-key.html", "_self");
}

document.addEventListener("DOMContentLoaded", () => {
    loadContacts();

    document.getElementById("contactForm").addEventListener("submit", e => {
        e.preventDefault();
        addContact();
    });
});

function loadContacts() {
    fetch(rootPath + "controller/get-contacts/?apiKey=" + apiKey)
        .then(res => res.json())
        .then(data => {
            let container = document.getElementById("contactsList");
            container.innerHTML = "";

            if (data.length === 0) {
                container.innerHTML = "<p>No contacts found.</p>";
                return;
            }

            data.forEach(contact => {
                let card = document.createElement("div");
                card.className = "contact-card";
                card.innerHTML = `<strong>${contact.name}</strong><br>${contact.phone}`;
                container.appendChild(card);
            });
        })
        .catch(() => {
            document.getElementById("contactsList").innerHTML = "Error loading contacts: Failed to fetch";
        });
}

function addContact() {
    let name = document.getElementById("name").value.trim();
    let phone = document.getElementById("phone").value.trim();

    if (!name || !phone) {
        alert("Please fill in all fields");
        return;
    }

    let formData = new FormData();
    formData.append("apiKey", apiKey);
    formData.append("name", name);
    formData.append("phone", phone);

    fetch(rootPath + "controller/add-contact/", {
        method: "POST",
        body: formData
    })
    .then(res => res.text())
    .then(data => {
        if (data == "1") {
            alert("Contact added successfully!");
            document.getElementById("contactForm").reset();
            loadContacts();
        } else {
            alert("Failed to add contact: " + data);
        }
    })
    .catch(err => alert("Error adding contact: " + err));
}
