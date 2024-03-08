#!/usr/bin/node

async function getProfile() {
    request.get('/user/me')
    .then((res) => {
        console.log(res)
        $("#greeting").text(`Hello ${res.username}`)
        $("#capital").text("$" + res.capital)
        request.get('/bot/' + res.bot_id)
        .then((bot) => {
            $("#daily-pnl").text(bot.today_pnl)
            $("#current-balance").text("$" + bot.balance)
            for (var item of bot.daily_pnl) {
                $("#performance-list").append(
                    `<li>${item.date}: ${item.msg}\n</li>`
                )
            }
            for (var item of bot.trades) {
                $("#todays-trades").append(
                    `<li>${item.date}: ${item.msg}\n</li>`
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
