for (let votingForm of document.querySelectorAll(".votingForm")) {
	let upVoteForm = votingForm.querySelector(".upVoteForm");
	let upVoteBtn = votingForm.querySelector(".upVoteBtn");
	let downVoteForm = votingForm.querySelector(".downVoteForm");
	let downVoteBtn = votingForm.querySelector(".downVoteBtn");
	makeFormAsync(upVoteForm, upVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerText = res["up_votes"];
		downVoteBtn.lastElementChild.innerText = res["down_votes"];
	});
	makeFormAsync(downVoteForm, downVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerText = res["up_votes"];
		downVoteBtn.lastElementChild.innerText = res["down_votes"];
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
