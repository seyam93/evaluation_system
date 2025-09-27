const addAppointmentBtn = document.getElementById("addAppointmentBtn");
const appointmentsContainer = document.getElementById("appointmentsContainer");

addAppointmentBtn.addEventListener("click", () => {
  const today = new Date().toISOString().split("T")[0];

  const section = document.createElement("div");
  section.className = "appointment-section";

  section.innerHTML = `
    <label>Date of Visit:</label>
    <input type="date" value="${today}" />

    <label>Diagnosis:</label>
    <input type="text" />

    <label>Pharmaceutical:</label>
    <input type="text" />

    <label>Required Tests:</label>
    <input type="text" />

    <label>Test Result:</label>
    <input type="text" />

    <label>Required Radiology:</label>
    <input type="text" />

    <label>Radiology Result:</label>
    <input type="text" />

    <label>Date of Second Visit:</label>
    <input type="date" />
  `;

  appointmentsContainer.appendChild(section);
});
