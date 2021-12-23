// utility functions

function makeFormAsync(form, btn, callBack) {
	form.addEventListener("submit", async function (e) {
		e.preventDefault();
		const formData = new FormData(form);
		btn.disabled = true;
		let res = await fetch(form.action, {
			method: "POST",
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": formData.csrfmiddlewaretoken,
			},
			body: formData,
		});
		btn.disabled = false;
		const status = res.status;
		res = await res.json();
		res.status = status;
		alert(res.message);
		callBack(res);
		return false;
	});
}

// theme change logic

const userThemeBtn = document.querySelector("#userThemeBtn");

function toogleTheme() {
	const isDark = document.body.classList.toggle("dark-mode");
	localStorage.setItem("slgIsDark", isDark);
	userThemeBtn.innerHTML = isDark ? "Dark Mode" : "Light Mode";
	userThemeBtn.previousElementSibling.classList.toggle("fa-sun-o");
	userThemeBtn.previousElementSibling.classList.toggle("fa-moon-o");
}

if (localStorage.getItem("slgIsDark") == "true") {
	toogleTheme();
}

userThemeBtn.addEventListener("click", toogleTheme);

// state and city drop down logic

const stateSelect = document.querySelector("#stateSelect");
const citySelect = document.querySelector("#citySelect");

Object.keys(stateCityJSON).forEach((state) => {
	const stateOption = document.createElement("option");
	stateOption.text = state;
	stateOption.value = state;
	stateSelect.append(stateOption);
});

stateSelect.addEventListener("change", () => {
	citySelect.length = 0;
	const selectCityOption = document.createElement("option");
	selectCityOption.value = "";
	selectCityOption.text = "Select City";
	citySelect.append(selectCityOption);
	const state = stateSelect.value;
	if (state != "") {
		stateCityJSON[state].forEach((city) => {
			const cityOption = document.createElement("option");
			cityOption.text = city;
			cityOption.value = city;
			citySelect.append(cityOption);
		});
	}
});

citySelect.addEventListener("change", () => {
	sessionStorage.setItem("locationState", stateSelect.value);
	sessionStorage.setItem("locationCity", citySelect.value);
	let appInfoPage = document.querySelector("#stateSelectAppInfo");
	if (appInfoPage != null) {
		stateSelectAppInfo.value = stateSelect.value;
		let changeEvent = new Event("change");
		stateSelectAppInfo.dispatchEvent(changeEvent);
		citySelectAppInfo.value = citySelect.value;
	}
});

// user location fetch logic

async function getLocation() {
	const res = await fetch("https://geolocation-db.com/json/");
	return res.json();
}

function setLocation(dict) {
	stateSelect.value = dict["state"];
	let changeEvent = new Event("change");
	stateSelect.dispatchEvent(changeEvent);
	citySelect.value = dict["city"];
	citySelect.dispatchEvent(changeEvent);
}

if (sessionStorage.getItem("locationState") != null) {
	stateSelect.value = sessionStorage.getItem("locationState");
	let changeEvent = new Event("change");
	stateSelect.dispatchEvent(changeEvent);
	citySelect.value = sessionStorage.getItem("locationCity");
} else {
	getLocation()
		.then((dict) => {
			setLocation(dict);
		})
		.catch((err) => {
			console.log(err);
		});
}
