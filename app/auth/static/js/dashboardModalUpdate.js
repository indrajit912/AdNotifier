function handleUpdateResponse(response) {
    // Handle the response...

    // Reload the page after a short delay (e.g., 1000 milliseconds or 1 second)
    setTimeout(function () {
        location.reload();
    }, 1000);
}

// Function that update the advertisement from user's dashboard
function updateDashboardAdvertisement(adId) {
    var updateAdvertisementUrl = window.updateAdvertisementUrl;

    // Get the values entered by the user
    var advTitle = document.querySelector('#adv-titleUpdate-' + adId).value;
    var advNum = document.querySelector('#adv-numUpdate-' + adId).value;
    var advUrl = document.querySelector('#adv-urlUpdate-' + adId).value;
    var advDesc = document.querySelector('#adv-descUpdate-' + adId).value;

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
    })
    .then(data => {
        // Handle the response, e.g., show a success message
        alert('Advertisement updated successfully!');
        // Close the modal
        var modal = new bootstrap.Modal(document.getElementById('updateModal' + adId));
        modal.hide();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}