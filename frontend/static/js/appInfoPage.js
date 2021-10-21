try {
	let upVoteForm = document.forms.namedItem("upVoteForm");
	let upVoteBtn = document.querySelector("#upVoteBtn");
	makeFormAsync(upVoteForm, upVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerHTML = res["up_votes"];
		downVoteBtn.lastElementChild.innerHTML = res["down_votes"];
	});
}
catch (err) {
	console.log(err)
}

try {
	let downVoteForm = document.forms.namedItem("downVoteForm");
	let downVoteBtn = document.querySelector("#downVoteBtn");
	makeFormAsync(downVoteForm, downVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerHTML = res["up_votes"];
		downVoteBtn.lastElementChild.innerHTML = res["down_votes"];
	});
}
catch (err) {
	console.log(err)
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