// Function to validate the email address entered by the user
function validateEmail() {
    // Get the value of the email input field by its ID
    var email = document.getElementById("Email").value;

    // Regular expression (regex) pattern to validate the email format
    // This pattern checks if the email has a general format like 'example@domain.com'
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    // Test the entered email against the regex pattern
    if (!emailRegex.test(email)) {
        // If the email does not match the regex, display a validation message to the user
        document.getElementById("validationMessage").innerHTML = "Please enter a valid email address!";
        
        // Return false to indicate that validation failed
        return false; 
    }

    // If the email is valid, return true to indicate successful validation
    return true;
}
