if (document.forms.namedItem("upVoteForm") != null) {
	let upVoteForm = document.forms.namedItem("upVoteForm");
	let upVoteBtn = document.querySelector("#upVoteBtn");
	makeFormAsync(upVoteForm, upVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerHTML = res["up_votes"];
		downVoteBtn.lastElementChild.innerHTML = res["down_votes"];
	});

	let downVoteForm = document.forms.namedItem("downVoteForm");
	let downVoteBtn = document.querySelector("#downVoteBtn");
	makeFormAsync(downVoteForm, downVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerHTML = res["up_votes"];
		downVoteBtn.lastElementChild.innerHTML = res["down_votes"];
	});
}

const stateSelectAppInfo = document.querySelector("#stateSelectAppInfo");
const citySelectAppInfo = document.querySelector("#citySelectAppInfo");

Object.keys(stateCityJSON).forEach((state) => {
	const stateOption = document.createElement("option");
	stateOption.text = state;
	stateOption.value = state;
	stateSelectAppInfo.append(stateOption);
});

stateSelectAppInfo.addEventListener("change", () => {
	citySelectAppInfo.length = 0;
	const selectCityOption = document.createElement("option");
	selectCityOption.value = "";
	selectCityOption.text = "Select City";
	citySelectAppInfo.append(selectCityOption);
	const state = stateSelectAppInfo.value;
	if (state != "") {
		stateCityJSON[state].forEach((city) => {
			const cityOption = document.createElement("option");
			cityOption.text = city;
			cityOption.value = city;
			citySelectAppInfo.append(cityOption);
		});
	}
});