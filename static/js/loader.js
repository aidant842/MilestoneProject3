/* $(document).ready(function(){
  $(window).onload(function(){
      alert('Loaded');
    $('.loader-bg').addClass('hidden');

  });
}); */

document.body.onload = function(){
    document.querySelector('.loader-bg').classList.add('hidden');
}