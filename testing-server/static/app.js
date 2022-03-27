'use strict';
const GOOGLE_BOOKS_API_KEY = "AIzaSyAjnuM0ma2Es__HV4ksbDqfNKpfRcdMzJo";

const listFormatter = new Intl.ListFormat("en", {
  style: "long",
  type: "conjunction",
});

try {
  const actionEl = document.querySelector("#action-select");
  const booksList = document.querySelector("#books-list");

  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

  const html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", {
    fps: 10,
    qrbox: 250,
  });

// displays books from the database to the website
  function displayBooksList() {
    fetch("./books")
      .then((res) => res.json())
      .then((isbns) => {
        document.querySelector(".error-el").innerHTML += isbns + "\n";
        booksList.innerHTML = "";

        for (let isbn of isbns) {
          fetch(
            `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}&key=${GOOGLE_BOOKS_API_KEY}`
          )
            .then((gbooksRes) => gbooksRes.json())
            .then((gbooksJson) => {
              const info = gbooksJson.items[0].volumeInfo;
              booksList.innerHTML += `
            <li class="list">
              <img src="${info.imageLinks.thumbnail}" style="width: auto; height: 160px;" />
              <h2>${info.title}</h2>
              <h3>${listFormatter.format(info.authors)}</h3>
              <details>
              <summary>About</summary>
              <p>${info.description}</p>
              </details>
            </li>`;
            })
            .catch((e) => {
              document.querySelector(".error-el").innerHTML +=
                e.toString() + "\n" + e.stack;
            });
        }
      })
      .catch((e) => {
        document.querySelector(".error-el").innerHTML +=
          e.toString() + "\n" + e.stack;
      });
  }

// method is called when a scan finishes successfully
  function onScanSuccess(decodedText, decodedResult) {
    const isbn = decodedText;
    fetch(`./books?isbn=${isbn}`, {
      method: actionEl.value === "add" ? "PUT" : "DELETE",
    }).then(() => {
      displayBooksList();
      html5QrcodeScanner.clear();
      html5QrcodeScanner.render(onScanSuccess);
    });
  }

// if the program is not run on safari, it will listen
  if (!isSafari) {
    const grammar = `
    #JSGF V1.0;
    
    grammar vxmlgram;
    
    public <command> =
        titles
        | piano
        | bookshelf
        | rainbow
        | music
        | remix;
    `;

    var SpeechRecognition = window.SpeechRecognition || webkitSpeechRecognition;
    var SpeechGrammarList =
      window.SpeechGrammarList || window.webkitSpeechGrammarList;
    var SpeechRecognitionEvent =
      window.SpeechRecognitionEvent || webkitSpeechRecognitionEvent;

    const reco = new SpeechRecognition();
    let speech = new SpeechSynthesisUtterance();
    if (SpeechGrammarList) {
      const recoList = new SpeechGrammarList();
      recoList.addFromString(grammar, 1);
      reco.grammars = recoList;
    }

    reco.continuous = false;
    reco.lang = "en-US";
    reco.interimResults = false;
    reco.maxAlternatives = 1;

    const listenBtn = document.querySelector(".listen");
    listenBtn.addEventListener("click", () => {
      reco.start();
      console.log("Ready to receive a color command.");
    });

    window.speechSynthesis.onvoiceschanged = () => {
      speech.voice = window.speechSynthesis.getVoices()[0];
    };
    speech.lang = "en";

    reco.addEventListener("result", (e) => {
      const said = e.results[0][0].transcript;
      fetch(`./voice-command?command=${encodeURIComponent(said)}`);
      console.log("we think you said: ", said);
      speech.text = said;
      window.speechSynthesis.speak(speech);
    });
  }

  displayBooksList();
  html5QrcodeScanner.render(onScanSuccess);
} catch (e) {
  document.querySelector(".error-el").innerHTML +=
    e.toString() + "\n" + e.stack;
}
