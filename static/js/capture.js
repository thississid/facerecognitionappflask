window.onload = function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const snap = document.getElementById('snap');
    const submitBtn = document.getElementById('submitBtn');
    const imageDataField = document.getElementById('image_data');

    // Get access to the webcam
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            video.srcObject = stream;
            video.play();
        });
    }

    // Trigger photo capture
    snap.addEventListener('click', function() {
        canvas.getContext('2d').drawImage(video, 0, 0, 320, 240);
        const dataURL = canvas.toDataURL('image/png');
        imageDataField.value = dataURL;
        submitBtn.style.display = 'block';
    });
};
