// For cross-page scripts

// This is one implementation of colour modes.
/* var DarkMode = false 
function changeColourMode() {
    switch (DarkMode){
    case false: document.documentElement.style.setProperty("background-color", '--background-colour-dark'), document.documentElement.style.setProperty("color", '--text-colour-dark'), DarkMode = true 
    case true: document.documentElement.style.setProperty("background-color", '--background-colour-light'), document.documentElement.style.setProperty("color", '--text-colour-light'), DarkMode = false
    }
}*/

// This is another. 
/*var mode = true
function modeTheme(){
    const root = document.querySelector(':root');
    if(mode==true){
        mode = false;
        root.style.setProperty('--main_bg-colour', '#ffdadf');
        root.style.setProperty('--main_text-colour', '#000');
        root.style.setProperty('--main_nav-text-colour', '#fff')
        root.style.setProperty('--tshad_1', '2px 2px 2px #fff, 2px -2px 2px #fff, -2px -2px 2px #fff, -2px 2px 2px #fff');
        root.style.setProperty('--tshad_2', '2px 2px 1px #000, 2px -2px 1px #000, -2px -2px 1px #000, -2px 2px 1px #000');
        document.getElementById('modeTog').innerText = '☾ ';
    }
    else{
        mode = true;
        root.style.setProperty('--main_bg-colour', '#000');
        root.style.setProperty('--main_text-colour', '#fff');
        root.style.setProperty('--main_nav-text-colour', '#000')
        root.style.setProperty('--tshad_1', '2px 2px 1px #000, 2px -2px 1px #000, -2px -2px 1px #000, -2px 2px 1px #000');
        root.style.setProperty('--tshad_2', '2px 2px 1px #fff, 2px -2px 1px #fff, -2px -2px 1px #fff, -2px 2px 1px #fff');
        document.getElementById('modeTog').innerText = '☉';
    }
}*/ 
