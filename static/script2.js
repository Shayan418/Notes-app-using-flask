window.onload = function () {
    fetch("https://ipinfo.io/json").then(
        (response) => response.json()
    ).then((jsonResponse) => {

        fetch(`${window.origin}/api/ip`, {
                method: "POST",
                dentials: "include",
                body: JSON.stringify(jsonResponse),
                cache: "no-cache",
                headers: new Headers({
                    "content-type": "application/json"
                })

            })
            .then(function (responce) {

                if (responce.status != 200) {
                    console.log(`Responce bad : ${responce.status}`)
                }

                responce.json().then(function (data) {
                    console.log(data)
                    document.getElementById("city").innerHTML = data.city
                    document.getElementById("temp").innerHTML = data.temp
                    document.getElementById("celcius").innerHTML = "&#8451"
                    if (data.day == 'false')
                        document.getElementById("celestialBody").src = "/static/moon-removebg-preview.png";
                    else
                        document.getElementById("celestialBody").src = "/static/sun-removebg-preview.png";
                })
            })
    })
};