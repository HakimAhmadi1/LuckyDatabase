$(document).ready(function() {

  var usernameValue = $('#username').val().trim();
  var emailValue = $('#email').val().trim();
  var passwordValue = $('#password').val().trim();

  function form_valid(){

    var result = true ;

    if (usernameValue.length < 1 || usernameValue.contains(" ") || usernameValue){
      $('#username').after('<span class="error">This field is required</span>');
    }

    var regEx = /^[A-Z0-9][A-Z0-9._%+-]{0,63}@(?:[A-Z0-9-]{1,63}\.){1,125}[A-Z]{2,63}$/;

    if (password.length < 8) {
      $('#password').after('<span class="error">Password must be at least 8 characters long</span>');
    }
  }
  
  $('#register-form').submit(function(event) {
    event.preventDefault();

    var username = $('#username').val();
    var email = $('#email').val();
    var password = $('#password').val();


    $.ajax({
      url: '../api/createuser/',
      type: 'POST',
      data: {
        'username': username,
        'email': email,
        'password': password
      },
      dataType: 'json',

      success: function(response) {

        window.location.href = '../'; 
      },
      error: function(error) {
        
        console.log(error);
        console.log('Registration failed:', error.responseText);
      }
    });
  });

});

