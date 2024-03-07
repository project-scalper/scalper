#!/usr/bin/node

$("#signup").on('click', () => {
    // console.log("Signup has been clicked")
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
        alert(res['msg'])
        window.localStorage.setItem("session_id", res['session_id'])
        window.location.href = 'static/start_bot.html';
    })
    .catch((err) => {
        alert(err['msg'])
    })
})

$("#login").on('click', () => {
    var username = $("#login-username").val()
    var password = $("#login-password").val()
    var payload = JSON.stringify({
        "username": username,
        "password": password,
    })
    request.post('/auth/login', payload)
    .then((res) => {
        alert(res['msg'])
        window.localStorage.setItem("session_id", res['session_id'])
        window.location.href = 'static/start_bot.html';
    })
    .catch((err) => {
        alert(err['msg'])
    })
})