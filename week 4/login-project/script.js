function verifyUser(event) {
  event.preventDefault(); // prevent form submission refresh

  const username = document.getElementById("usernameInput").value.trim();
  const password = document.getElementById("passwordInput").value.trim();
  const messageEl = document.getElementById("message");

  checkUserCreds(username, password, messageEl);
}

function checkUserCreds(username, password, messageEl) {
  // System credentials (hardcoded for demo)
  const systemUsername = "Bond";
  const systemPassword = "007";

  if (username === systemUsername && password === systemPassword) {
    messageEl.style.color = "#00ff00"; // green
    messageEl.textContent = "Correct. Logging you in...";
    // Here you can redirect or show the app content
  } else {
    messageEl.style.color = "#ff4c4c"; // red
    messageEl.textContent = "Username or password are incorrect";
  }
}
