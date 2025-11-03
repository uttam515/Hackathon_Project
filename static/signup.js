async function signup() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    // CHANGED: Using relative URL is better practice
    const response = await fetch("/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    if (response.ok) {
      // CHANGED: Redirect to login page after successful signup
      window.location.href = "/login";
    } else {
      alert(data.message || "Signup failed.");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Signup failed.");
  }
}