$(document).ready(function () {
  console.log("call.js loaded");

  var mediaRecorder;
  var audioChunks = [];
  var sessionId;
  var isRecording = false;
  var silenceCount = 0;
  var stopLoop = true; // Set initial state to true to avoid automatic start
  var audioContext;
  var analyser;
  var source;
  var stream;
  var isAudioPlaying = false; // Flag to check if generated audio is playing
  var audio; // Variable to hold the audio element
  const silenceThreshold = 500; // 0.5 seconds of silence to stop recording
  const silenceDelay = 100; // Check for silence every 100ms
  const minDecibels = -70; // Minimum decibels to consider as silence
  const silenceLimit = 10; // Number of consecutive silences required to stop recording

  // Function to start a new session
  async function startSession() {
    let response = await fetch('/start_session', { method: 'POST' });
    let data = await response.json();
    sessionId = data.session_id;
    console.log('Session started with ID:', sessionId);
  }

  // Function to play a sound
  function playSound(filename) {
    let sound = new Audio(`/static/${filename}`);
    sound.play().then(() => {
      console.log(`Playing sound: ${filename}`);
    }).catch(error => {
      console.error(`Error playing sound: ${filename}`, error);
    });
  }

  // Function to start recording audio
  async function startRecording() {
    if (!sessionId) {
      await startSession();
    }

    playSound('telefoon_start.mp3'); // Play start sound before recording

    if (!stream) {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    console.log("Recording started");

    audioChunks = [];
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      console.log("MediaRecorder stopped");
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
      await sendTranscriptionAsMessage(result.text);
    };
  }

  // Function to stop recording audio
  function stopRecording() {
    console.log("Stopping recording due to silence or user action");
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
    }
    isRecording = false;
    silenceCount = 0; // Reset silence count
  }

  // Toggle recording state
  function toggleRecording() {
    stopLoop = !stopLoop;

    if (stopLoop) {
      stopRecording();
      if (audio && !audio.paused) {
        audio.pause();
        audio.currentTime = 0; // Reset audio to start
        isAudioPlaying = false;
      }
      $("#start-phone-call").removeClass("active"); // Remove active class
    } else {
      startSpeechDetection();
      $("#start-phone-call").addClass("active"); // Add active class
    }
  }

  // Function to detect speech and start recording
  function startSpeechDetection() {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (!analyser) {
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      analyser.minDecibels = minDecibels;
    }

    async function getStream() {
      if (!stream) {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      return stream;
    }

    getStream().then((stream) => {
      if (!source) {
        source = audioContext.createMediaStreamSource(stream);
      }
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.fftSize);

      function detectSpeech() {
        if (!isAudioPlaying) { // Only detect speech if no audio is playing
          analyser.getByteFrequencyData(dataArray);
          let speechDetected = false;
          for (let i = 0; i < dataArray.length; i++) {
            if (dataArray[i] > 0) {
              speechDetected = true;
              break;
            }
          }
          console.log("Speech detected:", speechDetected);
          console.log("Data array:", dataArray);

          if (speechDetected && !isAudioPlaying) {
            if (!isRecording) {
              startRecording();
              isRecording = true;
            }
          } else {
            if (isRecording) {
              silenceCount++;
              if (silenceCount >= silenceLimit) {
                stopRecording();
              }
            }
          }
        }

        if (!stopLoop) {
          setTimeout(detectSpeech, silenceDelay);
        }
      }

      detectSpeech();
    }).catch((error) => {
      console.error("Error accessing audio stream:", error);
    });
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

    // Generate speech from the response
    await generateSpeech(result.response);
  }

  // Function to generate speech from text
  async function generateSpeech(text) {
    let response = await fetch('/generate_speech', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text }),
    });

    let result = await response.json();
    if (result.filename) {
      playAudio(result.filename);
    } else {
      console.error('Error generating speech:', result.error);
    }
  }

  // Function to delete audio
  async function deleteAudio(filename) {
    let response = await fetch(`/delete_audio/${filename}`, {
      method: 'DELETE',
    });

    if (response.ok) {
      console.log(`Deleted audio file: ${filename}`);
    } else {
      console.error(`Error deleting audio file: ${filename}`);
    }
  }

  // Function to play audio
  function playAudio(filename) {
    audio = new Audio(`/static/${filename}`);
    isAudioPlaying = true; // Set flag to indicate audio is playing
    audio.play().then(() => {
      console.log("Playing generated speech audio.");
      // Restart speech detection when the audio ends
      audio.onended = async () => {
        console.log("Generated speech audio ended.");
        isAudioPlaying = false; // Reset flag when audio ends
        await deleteAudio(filename); // Delete the audio file
        if (!stopLoop) {
          startSpeechDetection();
        }
      };
    }).catch(error => {
      console.error("Error playing audio:", error);
      isAudioPlaying = false; // Reset flag if there's an error playing audio
    });
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

  // Bind the toggle recording function to the phone icon button click
  $("#start-phone-call").on('click', function() {
    toggleRecording();
    if (stopLoop) {
      $("#start-phone-call").removeClass("active");
    } else {
      $("#start-phone-call").addClass("active");
    }
  });

  // Ensure everything is correctly initialized
  stopLoop = true;
});
