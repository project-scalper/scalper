#!/usr/bin/node

$("#signup").on('click', () => {
    var loader = document.getElementById("loader2")
    loader.style.display = 'block'

    var username = $("#username").val();
    var password = $("#password").val();
    var email = $("#email").val();

    var payload = JSON.stringify({
        "username": username,
        "password": password,
        "email": email,
    })
    request.post('/users', payload)
    .then((res) => {
        alert(res.msg)
        window.localStorage.setItem("session_id", res['session_id'])
        window.location.href = 'static/start_bot.html';
    })
    .catch((err) => {
        var loader = document.getElementById("loader")
        loader.style.display = 'none'
        if (err.responseJSON != undefined) {
            alert(err.responseJSON)
        } else {
            alert("An error was encountered")
        }
        console.log(err)
    })
})

$("#login").on('click', () => {
    // $("#loader").style.display = 'block';
    var loader = document.getElementById("loader")
    loader.style.display = 'block'

    var username = $("#login-username").val()
    var password = $("#login-password").val()
    var payload = JSON.stringify({
        "username": username,
        "password": password,
    })
    request.post('/auth/login', payload)
    .then((res) => {
        alert(res.msg)
        window.localStorage.setItem("session_id", res.session_id)
        if (res.has_bot === true) {
            window.location.href = "static/main.html";
        } else {
            window.location.href = 'static/start_bot.html';
        }
    })
    .catch((err) => {
        $("#loader").addClass('disappear')
        var loader = document.getElementById("loader")
        loader.style.display = 'none'
        if (err.responseJSON != undefined) {
            alert(err.responseJSON)
        } else {
            alert("An error was encountered")
        }
        console.log(err)
    })
})
