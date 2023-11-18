<div id="destinationHeading" style="font-weight: bold;"></div>
<div id="jsonOutput"></div>
<script>
  let useMetricUnits = false;
  let previousNavdirectionsUuid = null;
  let previousCurrentStepUuid = null;
  let jsonData = null;
  let initNav = 0;

  async function loadCurrentStep() {
    try {
      const response = await fetch('CurrentStep.json'); // Load CurrentStep.json

      if (!response.ok) {
        throw new Error('Failed to fetch CurrentStep.json.');
      }

      const json = await response.json();
      return json;
    } catch (error) {
      console.error('Error fetching or parsing CurrentStep.json:', error);
      return null;
    }
  }

  async function loadNavdirectionsData() {
    try {
      const response = await fetch('navdirections.json'); // Load navdirections.json

      if (!response.ok) {
        throw new Error(`Failed to fetch JSON file. Status: ${response.status}`);
      }

      const json = await response.json();

      // Check if the UUIDs match
      const match = json.uuid === previousCurrentStepUuid;

      previousNavdirectionsUuid = json.uuid;
      jsonData = json;
      initNav = 1;
      return jsonData;
    } catch (error) {
      console.error('Error fetching or parsing JSON data:', error);
      return jsonData; // Return the existing data on error
    }
  }

  async function fetchAndDisplayData() {
    const currentStepData = await loadCurrentStep();

    if (currentStepData !== null) {
      // Set the initial value for `currentStep` based on `CurrentStep.json`
      previousCurrentStepUuid = currentStepData.uuid;
    }

    if (currentStepData.uuid != previousNavdirectionsUuid) {
      await loadNavdirectionsData();
    }

    if (initNav === 0) {
      await loadNavdirectionsData(); 
    }

    // Check if jsonData is available and proceed
    if (jsonData) {
      // Access the data you need from the loaded JSON
      const firstRoute = jsonData.routes[0];
      const firstLeg = firstRoute.legs[0];
      const steps = firstLeg.steps;
      const destination = firstRoute.Destination;

      // Determine whether to use metric or imperial units based on the 'Metric' key
      useMetricUnits = firstRoute.Metric === true; // Removed `const` to update the global useMetricUnits

      // Display the 'destination' value on the webpage
      const destinationHeading = document.getElementById('destinationHeading');
      destinationHeading.textContent = `Destination: ${destination}`;

      // Display values from the steps
      const jsonOutputDiv = document.getElementById('jsonOutput');
      jsonOutputDiv.innerHTML = '';

      for (let i = currentStepData.CurrentStep; i < steps.length - 1; i++) {
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
    }
  }

  // Load `CurrentStep.json` initially
  loadCurrentStep().then((currentStepData) => {
    if (currentStepData !== null) {
      // Set the initial value for `currentStep` based on `CurrentStep.json`
      previousCurrentStepUuid = currentStepData.uuid;
      loadNavdirectionsData();
      // Fetch and display data initially
      fetchAndDisplayData();
    }
  });

  // Periodically fetch `CurrentStep.json` and display data every 5 seconds
  setInterval(fetchAndDisplayData, 5000); // Adjust the interval as needed (in milliseconds)
</script>
