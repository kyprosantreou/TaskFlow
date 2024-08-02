function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password");
    var passwordToggle = document.querySelector(".toggle-password");
    
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        passwordToggle.style.backgroundImage = "url('../static/Assets/eye-off.svg')";
    } else {
        passwordInput.type = "password";
        passwordToggle.style.backgroundImage = "url('../static/Assets/eye.svg')";
    }
}

function toggleRepeatPasswordVisibility() {
    var repeatPasswordInput = document.getElementById("repeat_password");
    var repeatPasswordToggle = document.querySelector(".toggle-repeat-password");
    
    if (repeatPasswordInput.type === "password") {
        repeatPasswordInput.type = "text";
        repeatPasswordToggle.style.backgroundImage = "url('../static/Assets/eye-off.svg')";
    } else {
        repeatPasswordInput.type = "password";
        repeatPasswordToggle.style.backgroundImage = "url('../static/Assets/eye.svg')";
    }
}
