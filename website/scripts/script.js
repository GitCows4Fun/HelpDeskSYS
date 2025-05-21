// For cross-page scripts
var DarkMode = false 
function changeColourMode() {
    switch (DarkMode){
    case false: document.documentElement.style.setProperty("background-color", '--background-colour-dark'), document.documentElement.style.setProperty("color", '--text-colour-dark'), DarkMode = true 
    case true: document.documentElement.style.setProperty("background-color", '--background-colour-light'), document.documentElement.style.setProperty("color", '--text-colour-light'), DarkMode = false
    }
}
