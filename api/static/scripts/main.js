#!/usr/bin/node

function loadBot(bot_id) {
    request.get('/bot/' + bot_id)
    .then((bot) => {
        $("#daily-pnl").text(bot.today_pnl.toFixed(2))
        $("#current-balance").text("$" + bot.balance.toFixed(2))
        $("#performance-list").html('')
        for (var item of bot.daily_pnl) {
            $("#performance-list").prepend(
                `<li>${item.date}: ${item.msg.toFixed(2)}\n</li>`
            )
        }
        $("#todays-trades").html('')
        for (var item of bot.trades) {
            var tm = item.date.split(', ')[1]
            $("#todays-trades").prepend(
                `<li>${tm}: ${item.msg}\n</li>`
            )
        }
    })
    .catch((err) => {
        console.log(err);
        var loader = document.getElementById('loader');
        if (loader != null) {
            loader.style.display = "none";
        }
        if (err.statusCode === 401) {
            alert("Your session has expired, please sign in again")
            window.location.href = "login.html"
        } else {
            alert("Error fetching bot");
        }
    })
}

async function getProfile() {
    request.get('/user/me')
    .then((res) => {
        console.log(res)
        $("#greeting").text(`Hello ${res.username}`)
        $("#capital").text("$" + res.capital)
        window.localStorage.setItem("bot_id", res.bot_id)
        loadBot(res.bot_id)
    })
    .catch((err) => {
        if (err.statusCode === 401) {
            alert("Your session has expired, please log in again to continue");
            window.location.href = 'login2.html'
        } else {
            alert("There was an error getting user info")
            console.log(err);
        }
    })
}

$("#reload").on('click', () => {
    bot_id = window.localStorage.getItem("bot_id");
    loadBot(bot_id);
})

Promise.all([getProfile()])
.then(() => {
    var loader = document.getElementById('preloader');
	if (loader != null) {
		loader.style.display = "none";
	}
})
