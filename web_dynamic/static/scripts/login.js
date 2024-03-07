#!/usr/bin/node

$("#signup").on('click', () => {
    console.log("Signup has been clicked")
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
        // windows.alert("Welcome back")
        alert(res['msg'])
        window.localStorage.setItem("session_id", res['session_id'])
        window.location.href = 'main.html';
    })
    .catch((err) => {
        alert(err['msg'])
    })
})