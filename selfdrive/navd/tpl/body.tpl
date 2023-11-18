<!DOCTYPE html>
<html lang="en" id="htmlElement">
<head>
  <meta charset="utf-8">
  <title>sunnypilot</title>
  <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
  <!-- UIkit CSS -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/css/uikit.min.css" />

  <!-- UIkit JS -->
  <script src="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/js/uikit.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/uikit@3.9.2/dist/js/uikit-icons.min.js"></script>

  <!-- Custom Styles for Dark Mode -->
  <style>
    #htmlElement.dark-mode,
    #htmlElement.dark-mode input,
    #htmlElement.dark-mode select {
      background-color: #121212; /* Dark background color */
      color: #ffffff; /* Light text color */
    }
  </style>

  <!-- Script to set default dark mode -->
  <script>
    document.addEventListener('DOMContentLoaded', function () {
      const htmlElement = document.getElementById('htmlElement');
      // Check if a 'darkMode' cookie exists and apply dark mode accordingly
      htmlElement.classList.toggle('dark-mode', getCookie('darkMode') !== 'false');
    });

    // Function to set a cookie with a given name, value, and expiration time
    function setCookie(name, value, days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/`;
    }

    // Function to get the value of a cookie with a given name
    function getCookie(name) {
      return document.cookie.split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1] || null;
    }
  </script>
</head>
<body style="margin: 0; padding: 0;">
  <div style="display: grid; place-items: center;">
    <div style="padding: 5px; font-weight: bold;" align="center"><a href="?reset=1"><img style="width: 100px; height: 100px; background-color: black;" src="logo.png"></a></div>
    {{content}}
  </div>
  <!-- Dark Mode Toggle Button -->
  <button class="uk-button uk-button-default uk-margin-small-right" onclick="toggleDarkMode()">Toggle Dark Mode</button>

  <script>
    function toggleDarkMode() {
      const htmlElement = document.getElementById('htmlElement');
      htmlElement.classList.toggle('dark-mode');
      // Save the dark mode preference to a cookie
      setCookie('darkMode', htmlElement.classList.contains('dark-mode'), 365);
    }
  </script>
</body>
</html>
