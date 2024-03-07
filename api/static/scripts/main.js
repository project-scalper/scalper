#!/usr/bin/node

function getProfile() {
    request.get('/user/me')
    .then((res) => {
        console.log(res)
        $("#greeting").text(`Hello ${res.username}`)
        $("#capital").text("$" + res.capital)
        request.get('/bot/' + res.bot_id)
        .then((bot) => {
            $("#daily-pnl").text(bot.daily_pnl)
            $("#current-balance").text("$" + bot.balance)
            for (var item of bot.trades) {
                $("#performance-list").append(
                    `<li>${item.date}: ${item.msg}\n</li>`
                )
            }
        })
        .catch(() => {
            alert("Error fetching bot")
        })
    })
}

getProfile()
