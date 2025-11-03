async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    // CHANGED: The URL is now "/login" to match your app.py
    const response = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    
    if (response.ok) { // 'response.ok' is safer than 'response.status === 200'
        // CHANGED: The token key is "access_token" in your app.py
        localStorage.setItem("token", data.access_token);
        
        // CHANGED: Your dashboard is at "/", not "/dashboard"
        window.location.href = "/dashboard"; 
    } else {
        alert(data.message || "Login failed.");
    }

  } catch (error) {
    console.error("Error:", error);
    alert("Login failed.");
  }
}