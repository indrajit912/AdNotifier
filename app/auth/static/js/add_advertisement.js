// addAdvertisement.js

$(document).ready(function () {
    var addAdvertisementUrl = window.addAdvertisementUrl;
    var dashboardUrl = window.dashboardUrl;
    // Add a click event listener to the button
    $('#addUserAdvertisementButton').on('click', function () {
      // Get the values from the form
      var advNumber = $('#adv-number').val();
      var webUrl = $('#adv-web-url').val();
  
      // Create an object with the form values
      var formData = {
        advertisement_number: advNumber,
        website_url: webUrl
      };
  
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
      });
    });
  });
  