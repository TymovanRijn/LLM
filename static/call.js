$(document).ready(function () {
  console.log("call.js loaded"); // Confirmation that the script is loaded

  var recognition;
  var isRecognizing = false; // Flag to check if speech recognition is active
  if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
  } else {
    console.log("Web Speech API is not supported in this browser.");
    return; // Exit the function if speech recognition is not supported
  }

  recognition.lang = "nl-NL";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  var synthesizer = window.speechSynthesis;

  $("#start-phone-call").click(function () {
    if (!isRecognizing) {
      startRecognition();
    } else {
      stopRecognition();
    }
  });

  recognition.onstart = function () {
    console.log("Spraakherkenning is actief. Je kunt nu spreken.");
  };

  recognition.onresult = function (event) {
    var transcript = event.results[0][0].transcript;
    console.log("Herkend: " + transcript);
    processVoiceMessage(transcript);
  };

  recognition.onerror = function (event) {
    console.error("Spraakherkenningsfout: " + event.error);
    if (event.error === "no-speech") {
      console.log("No speech detected, restarting recognition...");
      if (isRecognizing) {
        recognition.start(); // Restart recognition if still active
      }
    }
  };

  function startRecognition() {
    playStartSound();
    recognition.start();
    isRecognizing = true;
    $("#start-phone-call").addClass("active");
  }

  function stopRecognition() {
    recognition.stop();
    isRecognizing = false;
    $("#start-phone-call").removeClass("active");
  }

  function playStartSound() {
    var audio = new Audio("./static/telefoon_start.mp3");
    audio.play();
  }

  function processVoiceMessage(message) {
    console.log("Processing voice message:", message);
    $.ajax({
      url: "/send_message",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ message: message }),
      success: function (response) {
        console.log("Response from /send_message:", response);
        generateAndPlaySpeech(response.response);
        loadOfferteData(); // Call to update the offerte data after voice response
      },
      error: function (error) {
        console.error("Error sending voice message:", error);
      },
    });
  }

  function generateAndPlaySpeech(message) {
    console.log("Generating and playing speech for message:", message);
    $.ajax({
      url: "/generate_speech",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ text: message }),
      success: function (response) {
        console.log("Speech generated successfully. Filename:", response.filename);
        var audio = new Audio(`/static/${response.filename}`);
        audio.play();
        audio.onended = function() {
          // Remove the audio file after it has been played
          $.ajax({
            url: `/delete_audio/${response.filename}`,
            type: 'DELETE',
            success: function() {
              console.log(`${response.filename} deleted successfully.`);
            },
            error: function(error) {
              console.error(`Error deleting ${response.filename}:`, error);
            }
          });
          startRecognition();
        };
      },
      error: function (error) {
        console.error("Error generating speech:", error);
        console.log("Error details:", error);
        startRecognition(); // Restart recognition even if there is an error
      }
    });
  }

  function loadOfferteData() {
    $.ajax({
      url: "/get_offerte_data",
      type: "GET",
      cache: false,
      success: function (response) {
        console.log("Loaded offerte data:", response);
        $("#offerteTable tbody").empty();
        let totaalPrijs = 0;

        if (response.length > 0) {
          const item = response[0];

          Object.keys(item).forEach(function (key) {
            if (!key.startsWith("Prijs_") && key !== "ID" && key !== "m2") {
              var value = item[key] === null ? "N/A" : item[key];
              var prijsKey = "Prijs_" + key;
              var prijsValue = item[prijsKey]
                ? item[prijsKey].toFixed(2)
                : "N/A";
              if (item[prijsKey]) {
                totaalPrijs += parseFloat(item[prijsKey]);
              }

              var row = `<tr>
                     <td class="column-name">${key}</td>
                     <td class="column-value">${value}</td>
                     <td class="column-price">${prijsValue}</td>
                   </tr>`;
              $("#offerteTable tbody").append(row);
            }
          });

          if (item["m2"] !== null && item["m2"] !== undefined) {
            $("#offerteTable tbody").append(`<tr>
                                        <td class="column-name">m2</td>
                                        <td class="column-value">${item["m2"]}</td>
                                        <td class="column-price">-</td>
                                      </tr>`);
          }

          $("#offerteTable tbody").append(`<tr>
                                      <td class="column-name">Totaal</td>
                                      <td></td>
                                      <td class="column-price">${totaalPrijs.toFixed(
                                        2
                                      )}</td>
                                    </tr>`);
        }
      },
      error: function (xhr, status, error) {
        console.log("Error loading offerte data:", xhr, status, error);
      },
    });
  }
});
