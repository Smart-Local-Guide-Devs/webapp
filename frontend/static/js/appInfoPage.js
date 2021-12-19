for (const votingForm of document.querySelectorAll(".votingForm")) {
	const upVoteForm = votingForm.querySelector(".upVoteForm");
	const upVoteBtn = votingForm.querySelector(".upVoteBtn");
	const downVoteForm = votingForm.querySelector(".downVoteForm");
	const downVoteBtn = votingForm.querySelector(".downVoteBtn");
	makeFormAsync(upVoteForm, upVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerText = res.up_votes;
		downVoteBtn.lastElementChild.innerText = res.down_votes;
	});
	makeFormAsync(downVoteForm, downVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerText = res.up_votes;
		downVoteBtn.lastElementChild.innerText = res.down_votes;
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

if (sessionStorage.getItem("locationState") != null) {
	stateSelectAppInfo.value = sessionStorage.getItem("locationState")
	let changeEvent = new Event("change")
	stateSelectAppInfo.dispatchEvent(changeEvent)
	citySelectAppInfo.value = sessionStorage.getItem("locationCity")
}

citySelectAppInfo.addEventListener("change", () => {
	sessionStorage.setItem("locationState", stateSelectAppInfo.value)
	sessionStorage.setItem("locationCity", citySelectAppInfo.value)
})

const appReviewForm = document.forms.namedItem("appReviewForm");
const appReviewBtn = appReviewForm.querySelector("#appReviewBtn");
appReviewForm.addEventListener("submit", async function (e) {
	e.preventDefault();
	let formData = new FormData(appReviewForm);
	let queryChoices = [];
	const prefix = "query: ";
	const keys = Array.from(formData.keys());
	for (const key of keys) {
		if (key.startsWith(prefix)) {
			queryChoices.push({
				query: key.substring(prefix.length),
				choice: formData.get(key),
			});
			formData.delete(key);
		}
	}
	formData.append("query_choices", JSON.stringify(queryChoices));
	appReviewBtn.disabled = true;
	let res = await fetch(appReviewForm.action, {
		method: "POST",
		credentials: "same-origin",
		headers: {
			"X-CSRFToken": formData["csrfmiddlewaretoken"],
		},
		body: formData,
	});
	appReviewBtn.disabled = false;
	res = await res.json();
	console.log(res);
	alert(res.message);
	return false;
});
