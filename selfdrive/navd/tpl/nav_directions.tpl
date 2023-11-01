<div id="destinationHeading"  font-weight: bold;"></div>
<div id="jsonOutput"></div>
<script>
  let useMetricUnits = false;

  // Function to fetch and display JSON data
  async function fetchAndDisplayData() {
    try {
      const response = await fetch('navdirections.json'); // Provide the full path
      if (!response.ok) {
        throw new Error(`Failed to fetch JSON file. Status: ${response.status}`);
      }
      const jsonData = await response.json();

      // Access the first route's nested structure
      const firstRoute = jsonData.routes[0]; // Access the first route
      const firstLeg = firstRoute.legs[0]; // Access the first leg
      const steps = firstLeg.steps; // Access the steps array
      const destination = firstRoute.Destination; // Access the 'destination' value

      // Determine whether to use metric or imperial units based on the 'Metric' key
      const useMetricUnits = firstRoute.Metric === true;

      // Display the 'destination' value on the webpage
      const destinationHeading = document.getElementById('destinationHeading');
      destinationHeading.textContent = `Destination: ${destination}`;
      const currentStep = firstRoute.CurrentStep;
      // Display values from the steps
      const jsonOutputDiv = document.getElementById('jsonOutput');
      jsonOutputDiv.innerHTML = '';

      for (let i = currentStep; i < steps.length - 1; i++) {
        const step = steps[i];
        const instruction0 = steps[i].maneuver.instruction;
        const instruction = steps[i + 1].maneuver.instruction;
        let distance = step.distance;

        if (!useMetricUnits) {
          // Convert distance to miles if using imperial units
          distance = distance * 0.000621371;
        } else {
          distance = distance / 1000; // Convert meters to kilometers
        }

        // Display the values on the webpage
        if (i === 0) {
          jsonOutputDiv.innerHTML += `
            <p>${instruction0}</p>
            <hr>
          `;
        }
        jsonOutputDiv.innerHTML += `
          <p>In ${distance.toFixed(1)} ${useMetricUnits ? 'km' : 'miles'}: ${instruction}</p>
          <hr>
        `;
      }
    } catch (error) {
      console.error('Error fetching or parsing JSON data:', error);
      // Display error message on the webpage
      const jsonOutputDiv = document.getElementById('jsonOutput');
      jsonOutputDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
  }

  // Fetch and display data initially
  fetchAndDisplayData();

  // Periodically fetch and display data every 5 seconds
  setInterval(fetchAndDisplayData, 5000); // Adjust the interval as needed (in milliseconds)
</script>
