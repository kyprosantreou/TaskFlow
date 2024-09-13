// Function to open the sidebar
function openNav() {
  // Set the width of the sidebar element with ID "mySidebar" to 250px, making it visible
  document.getElementById("mySidebar").style.width = "250px";
  
  // Shift the main content area to the right by 250px to make room for the sidebar
  document.getElementById("main").style.marginLeft = "250px";
}
  
// Function to close the sidebar
function closeNav() {
  // Set the width of the sidebar element with ID "mySidebar" to 0px, hiding it
  document.getElementById("mySidebar").style.width = "0";
  
  // Reset the main content area margin to 0, returning it to its original position
  document.getElementById("main").style.marginLeft = "0";
}
