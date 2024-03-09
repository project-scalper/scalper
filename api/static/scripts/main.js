#!/usr/bin/node

async function getProfile() {
    request.get('/user/me')
    .then((res) => {
        console.log(res)
        $("#greeting").text(`Hello ${res.username}`)
        $("#capital").text("$" + res.capital)
        request.get('/bot/' + res.bot_id)
        .then((bot) => {
            $("#daily-pnl").text(bot.today_pnl.toFixed(2))
            $("#current-balance").text("$" + bot.balance.toFixed(2))
            for (var item of bot.daily_pnl) {
                $("#performance-list").prepend(
                    `<li>${item.date}: ${item.msg.toFixed(2)}\n</li>`
                )
            }
            for (var item of bot.trades) {
                $("#todays-trades").prepend(
                    tm = item.date.split(', ')[1]
                    `<li>${tm}: ${item.msg}\n</li>`
                )
            }
        })
        .catch((err) => {
            alert("Error fetching bot");
            console.log(err);
            if (err.statusCode === 401) {
                window.location.href = "login.html"
            }
        })
    })
}

Promise.all([getProfile()])
