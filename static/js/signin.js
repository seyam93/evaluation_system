document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
  
    const loginInput = document.getElementById('loginEmail').value.trim().toLowerCase();
    const password = document.getElementById('loginPassword').value;
  
    const storedEmail = localStorage.getItem('email');
    const storedUsername = localStorage.getItem('username');
    const storedPassword = localStorage.getItem('password');
  
    const isEmailOrUsernameMatch = 
      loginInput === storedEmail?.toLowerCase() || 
      loginInput === storedUsername?.toLowerCase();
  
    if (isEmailOrUsernameMatch && password === storedPassword) {
      alert("Login successful!");
      window.location.href = 'home.html';
    } else {
      alert("Incorrect email/username or password.");
    }
  });
  