async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("http://localhost:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    alert(data.message);

    if (response.status === 200) {
        localStorage.setItem("token",data.token);
        window.location.href = "/dashboard"; 
    }

  } catch (error) {
    console.error("Error:", error);
    alert("Login failed.");
  }
}