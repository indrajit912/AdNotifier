function handleUpdateResponse(response) {
    // Handle the response...

    // Reload the page after a short delay (e.g., 1000 milliseconds or 1 second)
    setTimeout(function () {
        location.reload();
    }, 1000);
}

function toggleupdateSpinner() {
    var spinner = document.getElementById('updateSpinner');
    spinner.classList.toggle('d-none');
  }

// Function that update the advertisement from the user's dashboard
function updateDashboardAdvertisement(adId) {
    var updateAdvertisementUrl = window.updateAdvertisementUrl;

    // Get the values entered by the user
    var advTitle = document.querySelector('#adv-titleUpdate-' + adId).value;
    var advNum = document.querySelector('#adv-numUpdate-' + adId).value;
    var advUrl = document.querySelector('#adv-urlUpdate-' + adId).value;
    var advDesc = document.querySelector('#adv-descUpdate-' + adId).value;

    // Show spinner before making the request
    toggleupdateSpinner();

    // Make a POST request to the server
    fetch(updateAdvertisementUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            adId: adId,
            advTitle: advTitle,
            advNum: advNum,
            advUrl: advUrl,
            advDesc: advDesc
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response...
        handleUpdateResponse(data);

        // Check for success or error
        if ('message' in data) {
            // Show success message
            alert('Advertisement updated successfully!');
            // Close the modal
            var modal = new bootstrap.Modal(document.getElementById('updateModal' + adId));
            modal.hide();
        } else if ('error' in data) {
            // Show error message
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
