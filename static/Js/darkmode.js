function toggleDarkMode() {
  fetch('/toggle_theme', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      }
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          document.body.classList.toggle('dark-mode', data.theme_mode === 'dark');
          const modeIcon = document.getElementById('modeIcon');
          const buttonText = document.getElementById('button-text');
          
          if (data.theme_mode === 'dark') {
              modeIcon.src = "{{ url_for('static', filename='Assets/moon.svg') }}";
              buttonText.textContent = "Light Mode";
          } else {
              modeIcon.src = "{{ url_for('static', filename='Assets/sun.svg') }}";
              buttonText.textContent = "Dark Mode";
          }
      }
  })
  .catch(error => console.error('Error:', error));
}

