function switchToRegister() {
    $('.loginBox').fadeOut('fast', function () {
        $('.registerBox').fadeIn('fast');
        $('.login-footer').fadeOut('fast', function () {
            $('.register-footer').fadeIn('fast');
        });
        $('.modal-title').html('Sign Up');
        $('.btn-google').html("<img src=\"https://img.icons8.com/color/16/000000/google-logo.png\"> Sign Up with Google");
        //$('.btn-twitter').html("<img style='width: 15px;' src=\"https://cdn.hipwallpaper.com/i/81/38/MOjkyA.png\"> Sign Up with Twitter");
    });

    $('.error').removeClass('alert alert-danger').html('');

}

function switchToLogin() {
    $('#loginModal .registerBox').fadeOut('fast', function () {
        $('.loginBox').fadeIn('fast');
        $('.register-footer').fadeOut('fast', function () {
            $('.login-footer').fadeIn('fast');
        });

        $('.modal-title').html('Login');
        $('.btn-google').html("<img src=\"https://img.icons8.com/color/16/000000/google-logo.png\"> Sign In with Google");
        //$('.btn-twitter').html("<img style='width: 15px;' src=\"https://cdn.hipwallpaper.com/i/81/38/MOjkyA.png\"> Sign In with Twitter");
    });

    $('.error').removeClass('alert alert-danger').html('');
}

function showLogin() {
    switchToLogin();
    setTimeout(function () {
        $('#loginModal').modal('show');
    }, 230);
}

function showRegister() {
    switchToRegister();
    setTimeout(function () {
        $('#loginModal').modal('show');
    }, 230);

}

$('#loginForm').submit(function (event) {
    event.preventDefault();

    const form = $(this);
    const URL = form.attr('action');

    $.ajax({
        method: 'POST',
        url: URL,
        data: form.serialize(),
        success: function () {
            window.location.replace("/");
        },
        error: function () {
            displayErrors();
        }
    });
});

$('#registerForm').submit(function (event) {
    event.preventDefault();

    const form = $(this);
    const URL = form.attr('action');

    $.ajax({
        method: 'POST',
        url: URL,
        data: form.serialize(),
        success: function (response) {
            $('#registerForm').html(response);
        },
        error: function () {
            window.location.replace('/');
        }
    });
});

function displayErrors() {
    $('.error').addClass('alert alert-danger').html("Invalid Email/Password.");
    $('input[type="password"]').val('');
}

