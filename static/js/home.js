window.onload = function() {
  const patientList = JSON.parse(localStorage.getItem("patients")) || [];
  displayPatients(patientList);
};

function displayPatients(patients) {
  const list = document.getElementById("patientList");
  list.innerHTML = "";

  patients.forEach((patient) => {
    const li = document.createElement("li");
    li.textContent = `${patient.name} - Age: ${patient.age} - Gender: ${patient.gender}`;
    list.appendChild(li);
  });
}

function searchPatients() {
  const query = document.getElementById("searchInput").value.toLowerCase();
  const allPatients = JSON.parse(localStorage.getItem("patients")) || [];
  const filtered = allPatients.filter(p => p.name.toLowerCase().includes(query));
  displayPatients(filtered);
}

   