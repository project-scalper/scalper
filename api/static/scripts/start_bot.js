#!/usr/bin/node

$(function getProfile() {
    request.get('/user/me')
    .then((res) => {
        if (res.has_bot === true) {
            window.location.href = 'main.html'
        }
    })
})

$("#create-bot").on('click', () => {
    var loader = document.getElementById("loader")
    loader.style.display = 'block'

    var capital = $("#capital").val()
    var apiKey = $("#apiKey").val()
    var secret = $("#secretKey").val()
    var exchange = "bybit"

    var payload = JSON.stringify({
        capital,
        exchange,
        keys: {apiKey, secret}
    })
    request.put('/user/me', payload)
    .then(() => {
        request.get('/create_bot')
        .then(() => {
            alert("Your bot has been created successfully")
            window.location.href = "main.html"
        })
        .catch(() => {
            // $("#loader").addClass('disappear')
            var loader = document.getElementById("loader")
            loader.style.display = 'none'
            alert("An error occured while creating your bot"), 400
        })
    })
    .catch((err) => {
        alert(err.responseJSON)
    })
})