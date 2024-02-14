// addAdvertisement.js

// Function to toggle the spinner
function toggleSpinner() {
  var spinner = document.getElementById('addNowSpinner');
  spinner.classList.toggle('d-none');
}

$(document).ready(function () {
  var addAdvertisementUrl = window.addAdvertisementUrl;
  var dashboardUrl = window.dashboardUrl;

  // Add a click event listener to the button
  $('#addUserAdvertisementButton').on('click', function () {
    // Get the values from the form
    var advTitle = $('#adv-title').val();
    var advNumber = $('#adv-number').val();
    var webUrl = $('#adv-web-url').val();
    var advDesc = $('#adv-description').val();

    // Create an object with the form values
    var formData = {
      title: advTitle,
      advertisement_number: advNumber,
      website_url: webUrl,
      description: advDesc
    };

    // Show spinner before making the request
    toggleSpinner();

    // Send a POST request using jQuery
    $.post(addAdvertisementUrl, formData, function (data) {
      // Handle the response data (if needed)
      console.log(data);

      // Check if the response indicates success (you may need to adjust this based on your server response)
      if (data.success) {
        // Redirect to auth.dashboard
        window.location.href = dashboardUrl;
      }
    })
    .fail(function (error) {
      console.error('Error:', error);
      window.location.href = dashboardUrl;
    })
    .always(function () {
      // Hide spinner after the request is complete
      // You may want to handle success or failure conditions appropriately
      // For simplicity, I'm hiding the spinner after a delay in this example
      setTimeout(function () {
        toggleSpinner();
      }, 7000); // Adjust the delay as needed
    });
  });
});
