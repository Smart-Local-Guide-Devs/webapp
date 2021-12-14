function makeFormAsync(form, btn, callBack) {
	form.addEventListener("submit", async function (e) {
		e.preventDefault();
		let formData = new FormData(form);
		btn.disabled = true;
		let res = await fetch(form.action, {
			method: "POST",
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": formData["csrfmiddlewaretoken"],
			},
			body: formData,
		});
		res = await res.json();
		alert(res.message);
		btn.disabled = false;
		callBack(res);
		return false;
	});
}

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