function videoToggle() {
  document.getElementById("video-button").classList.toggle("hidden");
}

function imageToggle() {
  document.getElementById("image-button").classList.toggle("hidden");
}


if(document.getElementById("image-button").onclick){
    videoToggle();
    imageToggle();
}
else if (document.getElementById("video-button").onclick){
    imageToggle();
    videoToggle();
}