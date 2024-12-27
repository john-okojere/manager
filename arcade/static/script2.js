// script.js
const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const status = document.getElementById("status");
const startBtn = document.getElementById("start-btn");

let faceMatcher;

// Load models for face recognition
async function loadModels() {
    const MODEL_URL = "/models";
    await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
    await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
    await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
}

// Start webcam video
async function startVideo() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((err) => console.error("Error accessing webcam: ", err));
}

// Detect and authenticate faces
async function detectFace() {
    const displaySize = { width: video.width, height: video.height };
    faceapi.matchDimensions(canvas, displaySize);

    const detections = await faceapi.detectAllFaces(
        video,
        new faceapi.TinyFaceDetectorOptions()
    ).withFaceLandmarks().withFaceDescriptors();

    const resizedDetections = faceapi.resizeResults(detections, displaySize);

    const labeledFaceDescriptors = await loadKnownFaces();
    faceMatcher = new faceapi.FaceMatcher(labeledFaceDescriptors, 0.6);

    const results = resizedDetections.map((d) =>
        faceMatcher.findBestMatch(d.descriptor)
    );

    results.forEach((result, i) => {
        const box = resizedDetections[i].detection.box;
        const drawBox = new faceapi.draw.DrawBox(box, { label: result.toString() });
        drawBox.draw(canvas);
        status.innerText = `Status: ${result.label === "unknown" ? "Not Recognized" : "Authenticated"}`;
    });
}

// Load known faces for comparison
async function loadKnownFaces() {
    const labels = ["Person1", "Person2"]; // Add known labels here
    return Promise.all(
        labels.map(async (label) => {
            const img = await faceapi.fetchImage(`/known_faces/${label}.jpg`);
            const detections = await faceapi.detectSingleFace(img)
                .withFaceLandmarks()
                .withFaceDescriptor();
            return new faceapi.LabeledFaceDescriptors(label, [detections.descriptor]);
        })
    );
}

// Event listeners
startBtn.addEventListener("click", detectFace);

// Initialize
(async () => {
    await loadModels();
    await startVideo();
})();
