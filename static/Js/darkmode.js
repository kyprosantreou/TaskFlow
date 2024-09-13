// Function to toggle between dark and light modes
function toggleDarkMode() {
  // Send a POST request to the '/toggle_theme' route to toggle the theme mode on the server
  fetch('/toggle_theme', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'  // Indicating that the content type being sent is JSON
      }
  })
  // Handle the response by converting it to JSON format
  .then(response => response.json())
  // Process the returned data
  .then(data => {
      // Check if the server-side operation was successful
      if (data.success) {
          // Toggle the 'dark-mode' class on the body based on the returned theme mode
          document.body.classList.toggle('dark-mode', data.theme_mode === 'dark');
          
          // Update the theme toggle button icon and text
          const modeIcon = document.getElementById('modeIcon');  // Get the icon element by ID
          const buttonText = document.getElementById('button-text');  // Get the text element by ID
          
          // If the mode is 'dark', switch to moon icon and change text to "Light Mode"
          if (data.theme_mode === 'dark') {
              modeIcon.src = "{{ url_for('static', filename='Assets/moon.svg') }}";  // Moon icon for dark mode
              buttonText.textContent = "Light Mode";  // Button text indicating next action
          } 
          // If the mode is 'light', switch to sun icon and change text to "Dark Mode"
          else {
              modeIcon.src = "{{ url_for('static', filename='Assets/sun.svg') }}";  // Sun icon for light mode
              buttonText.textContent = "Dark Mode";  // Button text indicating next action
          }
      }
  })
  // Log any error that occurs during the fetch operation
  .catch(error => console.error('Error:', error));
}
