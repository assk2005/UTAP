document.addEventListener("DOMContentLoaded", function() {

    let mediaRecorder = null;
    let recordedChunks = [];
    let stream = null;
    let countdownInterval = null;

    const preview = document.getElementById("preview");
    const sessionId = document.getElementById("session_id").value;
    const questionIndexInput = document.getElementById("question_index");

    const timer = document.getElementById("timer");
    const status = document.getElementById("status");

    const progressFill = document.getElementById("progress-fill");
    const progressText = document.getElementById("progress-text");

    const TOTAL_QUESTIONS = 5;


    // =========================
    // START RECORDING
    // =========================
    window.startRecording = async function() {

        if (mediaRecorder && mediaRecorder.state === "recording") return;

        recordedChunks = [];

        stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });

        preview.srcObject = stream;

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = function(event) {
            if (event.data.size > 0) recordedChunks.push(event.data);
        };

        mediaRecorder.start();

        let seconds = 60;
        timer.innerText = "Time left: 60 seconds";

        countdownInterval = setInterval(() => {

            seconds--;
            timer.innerText = "Time left: " + seconds + " seconds";

            if (seconds <= 0) {
                clearInterval(countdownInterval);
                stopRecording();
            }

        }, 1000);
    };


    // =========================
    // STOP RECORDING
    // =========================
    window.stopRecording = function() {

        if (!mediaRecorder || mediaRecorder.state !== "recording") return;

        clearInterval(countdownInterval);
        timer.innerText = "Processing answer...";

        mediaRecorder.stop();

        mediaRecorder.onstop = async function() {

            stream.getTracks().forEach(track => track.stop());

            const blob = new Blob(recordedChunks, { type: "video/webm" });

            const formData = new FormData();

            formData.append("audio", blob);
            formData.append("question", document.getElementById("question").innerText);
            formData.append("question_index", questionIndexInput.value);

            const response = await fetch(`/interview/upload/${sessionId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: formData
            });

            const data = await response.json();


            // =========================
            // CHECK IF INTERVIEW ENDED
            // =========================
            if (data.complete === true) {

                timer.innerText = "";
                status.innerText = "Interview Completed. Generating report...";

                if (progressFill) progressFill.style.width = "100%";
                if (progressText) progressText.innerText = "Interview Completed";

                setTimeout(() => {
                    window.location.href = "/interview/result/";
                }, 2000);

                return;
            }


            // =========================
            // UPDATE QUESTION
            // =========================
            document.getElementById("question").innerText = data.next_question;

            questionIndexInput.value = data.next_index;


            // =========================
            // UPDATE QUESTION COUNTER
            // =========================
            const currentQuestion = parseInt(data.next_index) + 1;

            if (progressText) {
                progressText.innerText =
                    "Question " + currentQuestion + " / " + TOTAL_QUESTIONS;
            }


            // =========================
            // UPDATE PROGRESS BAR
            // =========================
            const progressPercent =
                (parseInt(data.next_index) / TOTAL_QUESTIONS) * 100;

            if (progressFill) {
                progressFill.style.width = progressPercent + "%";
            }


            // =========================
            // SHOW ANALYTICS
            // =========================
            status.innerText =
                "Score: " + data.score +
                " | Emotion: " + data.emotion +
                " | Filler Words: " + data.filler_words +
                " | Speech Speed: " + data.speech_speed + " WPM";


            mediaRecorder = null;
            timer.innerText = "";


            // =========================
            // AUTO START NEXT QUESTION
            // =========================
            setTimeout(() => {
                startRecording();
            }, 5000);

        };
    };


    // =========================
    // CSRF TOKEN HELPER
    // =========================
    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie) {

            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (cookie.startsWith(name + "=")) {

                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                }
            }
        }

        return cookieValue;
    }

});