$(document).ready(function () {
  console.log("speech.js loaded");

  var mediaRecorder;
  var audioChunks = [];
  var sessionId;
  var isRecording = false;

  // Function to start a new session
  async function startSession() {
    let response = await fetch('/start_session', { method: 'POST' });
    let data = await response.json();
    sessionId = data.session_id;
    console.log('Session started with ID:', sessionId);
  }

  // Function to start recording audio
  async function startRecording() {
    if (!sessionId) {
      await startSession();
    }

    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    console.log("Recording started");

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      let audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
      let formData = new FormData();
      formData.append('audio', audioBlob, 'audio.mp3');

      let response = await fetch('/upload_audio', {
        method: 'POST',
        body: formData,
      });

      let result = await response.json();
      console.log('Transcription:', result.text);

      // Display the transcription as a message and send it to the chat endpoint
      displayTranscriptionMessage(result.text);
      sendTranscriptionAsMessage(result.text);

      audioChunks = [];
    };
  }

  // Function to stop recording audio
  function stopRecording() {
    mediaRecorder.stop();
    console.log("Recording stopped");
  }

  // Toggle recording state
  function toggleRecording() {
    if (isRecording) {
      stopRecording();
      isRecording = false;
    } else {
      startRecording();
      isRecording = true;
    }
  }

  // Function to send transcription as a message
  async function sendTranscriptionAsMessage(transcription) {
    let response = await fetch('/send_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: transcription }),
    });

    let result = await response.json();
    console.log('Chat response:', result.response);

    // Display the chat response in the chat container
    displayChatResponse(result.response);
  }

  // Function to display the transcription message
  function displayTranscriptionMessage(transcription) {
    $('<div class="message message-personal">' + transcription + '</div>').appendTo($(".mCSB_container")).addClass("new");
    updateScrollbar();
  }

  // Function to display the chat response
  function displayChatResponse(response) {
    $('<div class="message new"><figure class="avatar"><img src="./static/avatar_icon.png" /></figure>' + response + '</div>').appendTo($(".mCSB_container")).addClass("new");
    updateScrollbar();
  }

  // Function to update the scrollbar
  function updateScrollbar() {
    $(".messages-content").mCustomScrollbar("update").mCustomScrollbar("scrollTo", "bottom", {
      scrollInertia: 10,
      timeout: 0
    });
  }

  // Bind the toggle recording function to the microphone button click
  $("#start-recording").on('click', toggleRecording);
});
