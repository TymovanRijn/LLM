$(document).ready(function () {
  var recognition;
  if ("SpeechRecognition" in window) {
    recognition = new SpeechRecognition();
  } else if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
  } else {
    console.log("Speech recognition is not supported in this browser.");
    return;
  }

  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = function () {
    $("#recording-status").show();
  };

  recognition.onresult = function (event) {
    var speechResult = event.results[0][0].transcript;
    $(".message-input").val(speechResult);
    insertMessage(speechResult);
    $("#recording-status").hide();
  };

  recognition.onend = function () {
    $("#recording-status").hide();
  };

  recognition.onerror = function (event) {
    console.error("Speech recognition error", event.error);
    $("#recording-status")
      .text("Error: " + event.error)
      .show();
  };

  $("#start-recording").click(function () {
    if (!recognition) return; // Als recognition niet beschikbaar is, doe niets

    if ($(this).hasClass("active")) {
      recognition.stop();
      $(this).removeClass("active");
    } else {
      recognition.lang = "nl-NL";

      recognition.start();
      $(this).addClass("active");
    }
  });

  recognition.onend = function () {
    $("#start-recording").removeClass("active");
    $("#recording-status").hide();
  };
});
