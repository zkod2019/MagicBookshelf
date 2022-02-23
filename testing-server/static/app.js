const actionEl = document.querySelector("#action-select");
const booksList = document.querySelector("#books-list");

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

const GOOGLE_BOOKS_API_KEY = "AIzaSyAjnuM0ma2Es__HV4ksbDqfNKpfRcdMzJo";

const listFormatter = new Intl.ListFormat('en', { style: 'long', type: 'conjunction' });

displayBooksList();
html5QrcodeScanner.render(onScanSuccess);
