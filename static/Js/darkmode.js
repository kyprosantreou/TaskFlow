function toggleDarkMode() {
  var element = document.body;
  element.classList.toggle("dark-mode");

  var button = document.getElementById("toggle-theme-btn");
  var image = document.getElementById("modeIcon");

  if (element.classList.contains("dark-mode")) {
      image.src =  "../static/Assets/moon.svg";
      image.alt = "Dark Mode";
      document.getElementById("button-text").innerText = "Light Mode";
  } else {
      image.src = "../static/Assets/sun.svg";
      image.alt = "Dark Mode";
      document.getElementById("button-text").innerText = "Dark Mode";
  }
}
