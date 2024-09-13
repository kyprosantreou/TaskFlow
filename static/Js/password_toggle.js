// Function to toggle the visibility of the password field
function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password"); // Get the password input field
    var passwordToggle = document.querySelector(".toggle-password"); // Get the password visibility toggle button
    
    // Check the current type of the password input field
    if (passwordInput.type === "password") {
        passwordInput.type = "text"; // Change type to text to show password
        passwordToggle.style.backgroundImage = "url('../static/Assets/eye-off.svg')"; // Change icon to 'eye-off' to indicate password is visible
    } else {
        passwordInput.type = "password"; // Change type to password to hide password
        passwordToggle.style.backgroundImage = "url('../static/Assets/eye.svg')"; // Change icon to 'eye' to indicate password is hidden
    }
}

// Function to toggle the visibility of the repeat password field
function toggleRepeatPasswordVisibility() {
    var repeatPasswordInput = document.getElementById("repeat_password"); // Get the repeat password input field
    var repeatPasswordToggle = document.querySelector(".toggle-repeat-password"); // Get the repeat password visibility toggle button
    
    // Check the current type of the repeat password input field
    if (repeatPasswordInput.type === "password") {
        repeatPasswordInput.type = "text"; // Change type to text to show password
        repeatPasswordToggle.style.backgroundImage = "url('../static/Assets/eye-off.svg')"; // Change icon to 'eye-off' to indicate password is visible
    } else {
        repeatPasswordInput.type = "password"; // Change type to password to hide password
        repeatPasswordToggle.style.backgroundImage = "url('../static/Assets/eye.svg')"; // Change icon to 'eye' to indicate password is hidden
    }
}
