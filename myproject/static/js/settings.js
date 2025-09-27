const themeSelect = document.getElementById("themeSelect");
const languageSelect = document.getElementById("languageSelect");

window.onload = () => {
  // Load saved settings
  const savedTheme = localStorage.getItem("theme");
  const savedLanguage = localStorage.getItem("language");

  if (savedTheme) themeSelect.value = savedTheme;
  if (savedLanguage) languageSelect.value = savedLanguage;

  applyTheme(savedTheme || "light");
};

themeSelect.addEventListener("change", () => {
  const theme = themeSelect.value;
  localStorage.setItem("theme", theme);
  applyTheme(theme);
});

languageSelect.addEventListener("change", () => {
  const lang = languageSelect.value;
  localStorage.setItem("language", lang);
  alert("Language preference saved: " + lang);
});

function applyTheme(theme) {
  if (theme === "dark") {
    document.body.style.backgroundColor = "#222";
    document.body.style.color = "#fff";
  } else {
    document.body.style.backgroundColor = "#f4f4f4";
    document.body.style.color = "#000";
  }
}

  