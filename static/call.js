$(document).ready(function () {
  console.log("call.js loaded"); // Bevestiging dat het script is geladen

  var recognition;
  var isRecognizing = false; // Vlag om te controleren of spraakherkenning actief is
  if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
  } else {
    console.log("Web Speech API is not supported in this browser.");
    return; // Stop de functie als spraakherkenning niet wordt ondersteund
  }

  recognition.lang = "nl-NL";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  var synthesizer = window.speechSynthesis;

  $("#start-phone-call").click(function () {
    if (!isRecognizing) {
      playStartSound();
      recognition.start();
      isRecognizing = true;
      $(this).addClass("active");
    } else {
      recognition.stop();
      isRecognizing = false;
      $(this).removeClass("active");
    }
  });

  // Deze functie wordt geroepen wanneer de spraakherkenning start
  recognition.onstart = function () {
    console.log("Spraakherkenning is actief. Je kunt nu spreken.");
  };

  // Deze functie vangt het resultaat van de spraakherkenning
  recognition.onresult = function (event) {
    var transcript = event.results[0][0].transcript; // De herkende tekst
    console.log("Herkend: " + transcript);
    processVoiceMessage(transcript);
  };

  // Deze functie handelt eventuele fouten af in de spraakherkenning
  recognition.onerror = function (event) {
    console.error("Spraakherkenningsfout: " + event.error);
  };

  // Speel een startgeluid af wanneer de gebruiker kan beginnen met spreken
  function playStartSound() {
    var audio = new Audio("./static/telefoon_start.mp3"); // Vervang met het pad naar je startgeluid
    audio.play();
  }

  // Stuur de spraakopname naar de server en verwerk het antwoord
  function processVoiceMessage(message) {
    $.ajax({
      url: "/send_message",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ message: message }),
      success: function (response) {
        speakResponse(response.response);
      },
      error: function (error) {
        console.error(
          "Er is een fout opgetreden bij het versturen van het bericht:",
          error
        );
      },
    });
  }

  // Lees het antwoord voor met spraaksynthese
  function speakResponse(message) {
    var utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "nl-NL";
    utterance.onend = function () {
      // Speel het startgeluid af en start de spraakherkenning na het spreken
      if (isRecognizing) {
        playStartSound();
        recognition.start();
      }
    };
    synthesizer.speak(utterance);
  }
});
