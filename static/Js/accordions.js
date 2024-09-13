// Get all elements with the class "accordion1"
var acc = document.getElementsByClassName("accordion1");
var i;

// Loop through each element with the class "accordion1"
for (i = 0; i < acc.length; i++) {
    // Add a click event listener to each element
    acc[i].addEventListener("click", function() {
        // Toggle the "active1" class on the clicked element (to change styles, for example)
        this.classList.toggle("active1");

        // Get the next sibling element (the panel that will be shown/hidden)
        var panel = this.nextElementSibling;

        // Check the current display style of the panel and toggle it between "block" and "none"
        if (panel.style.display === "block") {
            panel.style.display = "none";  // If it's currently shown, hide it
        } else {
            panel.style.display = "block"; // If it's hidden, show it
        }
    });
}

// Get all elements with the class "accordion2"
var acc = document.getElementsByClassName("accordion2");

// Loop through each element with the class "accordion2"
for (i = 0; i < acc.length; i++) {
    // Add a click event listener to each element
    acc[i].addEventListener("click", function() {
        // Toggle the "active2" class on the clicked element
        this.classList.toggle("active2");

        // Get the next sibling element (the panel to be shown/hidden)
        var panel = this.nextElementSibling;

        // Check the current display style of the panel and toggle it between "block" and "none"
        if (panel.style.display === "block") {
            panel.style.display = "none";  // If it's currently shown, hide it
        } else {
            panel.style.display = "block"; // If it's hidden, show it
        }
    });
}

// Get all elements with the class "accordion3"
var acc = document.getElementsByClassName("accordion3");

// Loop through each element with the class "accordion3"
for (i = 0; i < acc.length; i++) {
    // Add a click event listener to each element
    acc[i].addEventListener("click", function() {
        // Toggle the "active3" class on the clicked element
        this.classList.toggle("active3");

        // Get the next sibling element (the panel to be shown/hidden)
        var panel = this.nextElementSibling;

        // Check the current display style of the panel and toggle it between "block" and "none"
        if (panel.style.display === "block") {
            panel.style.display = "none";  // If it's currently shown, hide it
        } else {
            panel.style.display = "block"; // If it's hidden, show it
        }
    });
}
