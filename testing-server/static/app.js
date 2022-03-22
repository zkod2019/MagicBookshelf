const actionEl = document.querySelector("#action-select");
const booksList = document.querySelector("#books-list");

//var SpeechRecognition = window.SpeechRecognition || webkitSpeechRecognition;
//var SpeechGrammarList = window.SpeechGrammarList || webkitSpeechGrammarList;
//var SpeechRecognitionEvent =
//  window.SpeechRecognitionEvent || webkitSpeechRecognitionEvent;

const html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", {
  fps: 10,
  qrbox: 250,
});

function displayBooksList() {
  fetch('./books').then(res => res.json()).then(isbns => {
    for (let isbn of isbns)  {
      fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}&key=${GOOGLE_BOOKS_API_KEY}`)
        .then(gbooksRes => gbooksRes.json())
        .then(gbooksJson => {
          const info = gbooksJson.items[0].volumeInfo;
          booksList.innerHTML += `
            <li>
              <img src="${info.imageLinks.thumbnail}"/>
              <h2>${info.title}</h2>
              <p>${info.description}</p>
              <p>${listFormatter.format(info.authors)}</p>
            </li>`
        })
    }
  })

}

function onScanSuccess(decodedText, decodedResult) {
  const isbn = decodedText;
  fetch(`./books?isbn=${isbn}`, {method: actionEl.value === 'add' ? 'PUT' : 'DELETE'})
    .then(() => {
      displayBooksList();
      html5QrcodeScanner.clear();
      html5QrcodeScanner.render(onScanSuccess);
    });
}
/*
const grammar = `
#JSGF V1.0;

grammar vxmlgram;

public <command> =
    titles
    | play chill
    | play intense
    | rainbow
    | matrix
    | remix;
`;


const reco = new SpeechRecognition();
const recoList = new SpeechGrammarList();
let speech = new SpeechSynthesisUtterance();

recoList.addFromString(grammar, 1);
reco.grammars = recoList;

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
  fetch(`./voice-command?command=${encodeURIComponent(said)}`)
  console.log('we think you said: ', said)
  speech.text = said;
  window.speechSynthesis.speak(speech);
});
*/
const GOOGLE_BOOKS_API_KEY = "AIzaSyAjnuM0ma2Es__HV4ksbDqfNKpfRcdMzJo";

const listFormatter = new Intl.ListFormat('en', { style: 'long', type: 'conjunction' });

displayBooksList();
html5QrcodeScanner.render(onScanSuccess);
