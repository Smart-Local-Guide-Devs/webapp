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

// $("#stateSelect").change(function () {
// 	$("#citySelect").empty();
// 	$("#citySelect").append('<option value="">Select City</option>');
// 	const state = $(this).val();
// 	if (state != "") {
// 		stateCityJSON[state].forEach((city) => {
// 			if (userState == state && userCity == city)
// 				$("#citySelect").append(`<option selected>${city}</option>`);
// 			else $("#citySelect").append(`<option >${city}</option>`);
// 		});
// 	}
// });
