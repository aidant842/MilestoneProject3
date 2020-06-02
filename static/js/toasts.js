$(document).ready(function(){
let message = $('.message').text();
if(message){
M.toast({html: message}, 2000);
}
});
