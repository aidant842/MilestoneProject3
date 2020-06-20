/* Credit to stackoverflow user Der Hochstapler */
function check(input) {
  if (input.value != document.getElementById("password").value) {
    input.setCustomValidity("Password Must be Matching.");
  } else {
    // input is valid -- reset the error message
    input.setCustomValidity("");
  }
}
