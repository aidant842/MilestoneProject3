function videoToggle() {
  document.getElementById("game-img").classList.toggle("hidden");
}

function imageToggle() {
  document.getElementById("vid-con").classList.toggle("hidden");
}


document.getElementById("image-button").onclick = function(){
    if(document.getElementById("game-img").classList.contains("hidden")){
    videoToggle();
    imageToggle();
    }
};

document.getElementById("video-button").onclick = function(){
    if(document.getElementById("vid-con").classList.contains("hidden")){
    imageToggle();
    videoToggle();
    }
};

function buttonToggle(){
    document.getElementById("button-con").classList.toggle("hidden");
}

document.getElementById("game-vid").onclick = function(){
    buttonToggle();
};