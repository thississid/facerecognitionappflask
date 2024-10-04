// capture.js
window.onload = function () {
    var video = document.getElementById('video');
    var canvas = document.getElementById('canvas');
    var snap = document.getElementById('snap');
    var submitBtn = document.getElementById('submitBtn');
    var imageData = document.getElementById('image_data');

    // Get access to the camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.log("An error occurred: " + err);
        });

    // Trigger photo take
    snap.addEventListener("click", function () {
        var context = canvas.getContext('2d');
        canvas.style.display = 'block';
        context.drawImage(video, 0, 0, 320, 240);

        var dataURL = canvas.toDataURL('image/png');
        imageData.value = dataURL; // Set the hidden input with the base64 data
        submitBtn.style.display = 'block'; // Show submit button
    });
};
