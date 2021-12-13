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
