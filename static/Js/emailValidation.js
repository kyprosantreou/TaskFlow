function validateEmail() {
    var email = document.getElementById("Email").value;
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
        document.getElementById("validationMessage").innerHTML = "Please enter a valid email address!";
        return false; 
    }

    return true;
}
