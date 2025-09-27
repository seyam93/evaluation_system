// medications.js
document.addEventListener("DOMContentLoaded", () => {
    const medForm = document.getElementById("medicationForm");
    const medList = document.getElementById("medicationsList");
    const searchInput = document.getElementById("searchInput");
  
    let medications = [];
  
    medForm.addEventListener("submit", (e) => {
      e.preventDefault();
  
      const name = document.getElementById("medName").value.trim();
      const company = document.getElementById("medCompany").value.trim();
      const details = document.getElementById("medDetails").value.trim();
  
      if (!name || !company || !details) return;
  
      const newMed = {
        name,
        company,
        details,
        date: new Date().toLocaleDateString(),
      };
  
      medications.push(newMed);
      displayMedications(medications);
      medForm.reset();
    });
  
    searchInput.addEventListener("input", () => {
      const filtered = medications.filter((med) =>
        med.name.toLowerCase().includes(searchInput.value.toLowerCase())
      );
      displayMedications(filtered);
    });
  
    function displayMedications(list) {
      medList.innerHTML = "";
      list.forEach((med) => {
        const div = document.createElement("div");
        div.className = "med-item";
        div.innerHTML = `<strong>${med.name}</strong> (${med.company})<br><em>${med.date}</em><br><p>${med.details}</p>`;
        medList.appendChild(div);
      });
    }
  });
  