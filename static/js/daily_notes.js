const notesContainer = document.getElementById("notesContainer");
const addNoteBtn = document.getElementById("addNoteBtn");

// Load saved notes from localStorage
let notes = JSON.parse(localStorage.getItem("dailyNotes")) || [];

function saveNotes() {
  localStorage.setItem("dailyNotes", JSON.stringify(notes));
}

function displayNotes() {
  notesContainer.innerHTML = "";
  notes.forEach((note, index) => {
    const noteDiv = document.createElement("div");
    noteDiv.className = "note";

    const date = document.createElement("strong");
    date.textContent = `Date: ${note.date}`;
    noteDiv.appendChild(date);

    const textarea = document.createElement("textarea");
    textarea.value = note.text;
    textarea.addEventListener("input", () => {
      notes[index].text = textarea.value;
      saveNotes();
    });

    noteDiv.appendChild(textarea);
    notesContainer.appendChild(noteDiv);
  });
}

addNoteBtn.addEventListener("click", () => {
  const today = new Date().toLocaleDateString();
  notes.push({ date: today, text: "" });
  saveNotes();
  displayNotes();
});

displayNotes();
